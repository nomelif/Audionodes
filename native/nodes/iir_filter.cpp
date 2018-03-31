#include "nodes/iir_filter.hpp"

IIRFilter::IIRFilter() :
    Node(
      SocketTypeList(4, SocketType::audio),
      {SocketType::audio},
      {PropertyType::select, PropertyType::integer}
    )
{
  set_property_value(Properties::poles, 2);
}

IIRFilter::Coeffs::Coeffs() {
  a[0] = 1;
  b[0] = 1;
  for (size_t i = 1; i < max_coeff; ++i) {
    a[i] = 0;
    b[i] = 0;
  }
}

void IIRFilter::apply_bundle_universe_changes(const Universe &universe) {
  universe.apply_delta(bundles);
}

void IIRFilter::Coeffs::apply(Biquad biq) {
  if (count+2 >= max_coeff) return;
  for (size_t i = count-1; i < max_coeff /* underflow */; --i) {
    double val_a = a[i], val_b = b[i];
    a[i] = val_a*biq.a[0];
    a[i+1] += val_a*biq.a[1];
    a[i+2] += val_a*biq.a[2];
    b[i] = val_b*biq.b[0];
    b[i+1] += val_b*biq.b[1];
    b[i+2] += val_b*biq.b[2];
  }
  count += 2;
}

void IIRFilter::Coeffs::correct_gain(Modes mode) {
  double asum = 0, bsum = 0;
  int alt = 1;
  for (size_t i = 0; i < max_coeff; ++i) {
    asum += alt*a[i];
    if (i) bsum += alt*a[i];
    if (mode == Modes::high_pass) alt *= -1;
  }
  double gain = asum/(1-bsum);
  for (size_t i = 0; i < max_coeff; ++i) {
    a[i] /= gain;
  }
}

#include <iostream>
void IIRFilter::Filter::process(const Chunk& input, Chunk& output) {
  for (size_t i = 0; i < N; ++i) {
    double sum = input[i]*coeffs.a[0];
    for (size_t k = 1; k < std::min(coeffs.count, in_hist.size()+1); ++k) {
      sum += coeffs.a[k]*in_hist.back(k-1);
      sum -= coeffs.b[k]*out_hist.back(k-1);
    }
    std::cout << sum << std::endl;
    in_hist.push_back(input[i]);
    out_hist.push_back(sum);
    output[i] = sum;
  }
}

void IIRFilter::process(NodeInputWindow &input) {
  size_t n = input.get_channel_amount();
  AudioData::PolyWriter output(output_window[0]);
  output.resize(n);
  Modes mode = static_cast<Modes>(get_property_value(Properties::mode));
  int poles = get_property_value(Properties::poles);
  if (poles < 0) poles = 0;
  if (poles > max_poles) poles = max_poles;
  for (size_t i = 0; i < n; ++i) {
    SigT
      cutoff = input[InputSockets::cutoff][i][0],
      resonance = input[InputSockets::resonance][i][0],
      rolloff = input[InputSockets::rolloff][i][0];
    const Chunk &sig_in = input[InputSockets::input][i];
    Chunk &sig_out = output[i];
    Filter n_filter, &o_filter = bundles[i];
    n_filter.in_hist = o_filter.in_hist;
    n_filter.out_hist = o_filter.out_hist;
    // Calculate coefficients
    for (size_t pole_i = 0; pole_i < poles; ++pole_i) {
      double rot = M_PI/2+(pole_i+0.5)/poles*M_PI/2;
      double real = std::cos(rot), imag = std::sin(rot);
      double M = std::pow(real, 2)+std::pow(imag, 2);
      std::cout << "M=" << M << std::endl;
      static const double T = 2*std::tan(0.5);
      static const double T2 = pow(T, 2);
      std::cout << "T=" << T << std::endl;
      double D = 4-4*real*T+M*T2;
      std::cout << "D=" << D << std::endl;
      double k;
      if (mode == Modes::low_pass) {
        k = std::sin(0.5-cutoff/2)/std::sin(0.5+cutoff/2);
      } else {
        k = -std::cos(0.5+cutoff/2)/std::cos(0.5-cutoff/2);
      }
      std::cout << "k=" << k << std::endl;
      double k2 = pow(k, 2);
      Biquad biq{
        {T2/D, 2*T2/D, T2/D},
        {1, (8-2*M*T2)/D, (-4-4*real*T-M*T2)/D}
      };
      double S = 1+biq.b[1]*k-biq.b[2]*k2;
      biq = {
        {(biq.a[0]-biq.a[1]*k+biq.a[2]*k2)/S,
        (-2*biq.a[0]*k+(1+k2)*biq.a[1]-2*biq.a[2]*k)/S,
        (biq.a[0]*k2-biq.a[1]*k+biq.a[2])/S},
        {1, -(2*k+(1+k2)*biq.b[1]-2*biq.b[2]*k)/S, -(-k2-biq.b[1]*k+biq.b[2])/S}
      };
      if (mode == Modes::high_pass) {
        biq.a[1] *= -1;
        biq.b[1] *= -1;
      }
      n_filter.coeffs.apply(biq);
    }
    //n_filter.coeffs.correct_gain(mode);
    std::cout << "final a: ";
    for (int x = 0; x < n_filter.coeffs.count; ++x) {
      std::cout << n_filter.coeffs.a[x] << " ";
    }
    std::cout << std::endl;
    std::cout << "final b: ";
    for (int x = 0; x < n_filter.coeffs.count; ++x) {
      std::cout << n_filter.coeffs.b[x] << " ";
    }
    std::cout << std::endl;
    n_filter.initialized = true;
    if (o_filter.initialized) {
      std::cout << "interp" << std::endl;
      // Interpolate between old and new
      Chunk o_out, n_out;
      o_filter.process(sig_in, o_out);
      n_filter.process(sig_in, n_out);
      for (size_t j = 0; j < N; ++j) {
        sig_out[j] = (o_out[j]*(N-j)+n_out[j]*j)/N;
      }
    } else {
      // Only new
      n_filter.process(sig_in, sig_out);
    }
    o_filter = n_filter;
  }
}
