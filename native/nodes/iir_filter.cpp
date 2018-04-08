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

void IIRFilter::apply_bundle_universe_changes(const Universe &universe) {
  universe.apply_delta(bundles);
}

bool IIRFilter::Filter::equivalent(Modes mode_, int poles_, SigT cutoff_, SigT resonance_, SigT rolloff_) const {
  return mode == mode_ && poles == poles_ && cutoff == cutoff_ && resonance == resonance_ && rolloff == rolloff_;
}

IIRFilter::Filter::Filter(Modes mode, int poles, SigT cutoff, SigT resonance, SigT rolloff) :
    mode(mode), poles(poles), cutoff(cutoff), resonance(resonance), rolloff(rolloff),
    initialized(true)
{
  resonance = std::pow(resonance, 1./poles);
  // Calculate coefficients
  for (size_t pole_i = 0; pole_i < poles; ++pole_i) {
    FSigT rot;
    if (resonance >= 1) {
      rot = M_PI/2+(pole_i+0.5)/poles*M_PI/2/resonance;
    } else {
      rot = M_PI-(pole_i+0.5)/poles*M_PI/2*resonance;
    }
    FSigT real = std::cos(rot), imag = std::sin(rot)/rolloff;
    FSigT M = std::pow(real, 2)+std::pow(imag, 2);
    static const FSigT T = 2*std::tan(0.5);
    static const FSigT T2 = pow(T, 2);
    FSigT D = 4-4*real*T+M*T2;
    FSigT k;
    if (mode == Modes::low_pass) {
      k = std::sin(0.5-cutoff/2)/std::sin(0.5+cutoff/2);
    } else {
      k = -std::cos(0.5+cutoff/2)/std::cos(0.5-cutoff/2);
    }
    FSigT k2 = pow(k, 2);
    DirectForm biq = {
      {T2/D, 2*T2/D, T2/D},
      {1, (8-2*M*T2)/D, (-4-4*real*T-M*T2)/D}
    };
    FSigT S = 1+biq.b[1]*k-biq.b[2]*k2;
    biq = {
      {(biq.a[0]-biq.a[1]*k+biq.a[2]*k2)/S,
      (-2*biq.a[0]*k+(1+k2)*biq.a[1]-2*biq.a[2]*k)/S,
      (biq.a[0]*k2-biq.a[1]*k+biq.a[2])/S},
      {1, (2*k+(1+k2)*biq.b[1]-2*biq.b[2]*k)/S, (-k2-biq.b[1]*k+biq.b[2])/S}
    };
    if (mode == Modes::high_pass) {
      biq.a[1] *= -1;
      biq.b[1] *= -1;
    }
    biq.correct_gain(mode);
    Lattice &lat = biquads[pole_i];
    lat = {{biq.b[2], biq.b[1]/(1-biq.b[2])}};
    lat.v[0] = biq.a[2];
    lat.v[1] = biq.a[1]+lat.v[0]*biq.b[1];
    lat.v[2] = biq.a[0]+lat.v[0]*biq.b[2]+lat.v[1]*lat.k[1];
  }
}

void IIRFilter::DirectForm::correct_gain(Modes mode) {
  FSigT gain;
  if (mode == Modes::low_pass) {
    gain = (a[0]+a[1]+a[2])/(1-b[1]-b[2]);
  } else {
    gain = (a[0]-a[1]+a[2])/(1+b[1]-b[2]);
  }
  a[0] /= gain; a[1] /= gain; a[2] /= gain;
}


void IIRFilter::Filter::copy_state(const Filter &from) {
  if (!from.initialized || from.poles != poles || from.mode != mode) {
    // Incompatible structure
    for (size_t i = 0; i < poles; ++i) {
      biquads[i].state[0] = 0;
      biquads[i].state[1] = 0;
    }
    return;
  }
  for (size_t i = 0; i < poles; ++i) {
    biquads[i].state[0] = from.biquads[i].state[0];
    biquads[i].state[1] = from.biquads[i].state[1];
    old_biquads[i] = from.biquads[i];
  }
}

IIRFilter::Lattice IIRFilter::Lattice::interpolate(const Lattice& a, const Lattice& b, FSigT rat) {
  Lattice n;
  for (size_t i = 0; i < 2; ++i) {
    n.k[i] = a.k[i]*(1-rat)+b.k[i]*rat;
  }
  for (size_t i = 0; i < 3; ++i) {
    n.v[i] = a.v[i]*(1-rat)+b.v[i]*rat;
  }
  return n;
}

void IIRFilter::Filter::process(const Chunk& input, Chunk& output, bool interpolate) {
  for (size_t i = 0; i < N; ++i) {
    FSigT in = input[i];
    for (size_t j = 0; j < poles; ++j) {
      Lattice &l = biquads[j];
      Lattice c = interpolate ? 
        Lattice::interpolate(old_biquads[j], biquads[j], FSigT(i)/N) : l;
      FSigT nS0 = in+c.k[0]*l.state[1]+c.k[1]*l.state[0];
      FSigT nS1 = l.state[0]-c.k[1]*nS0;
      FSigT out = c.v[2]*nS0+c.v[1]*nS1+c.v[0]*(l.state[1]-c.k[0]*(c.k[0]*l.state[1]+in));
      l.state[0] = nS0;
      l.state[1] = nS1;
      in = out;
    }
    output[i] = in;
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
    cutoff = cutoff/RATE*2;
    // Limit around 10 Hz, below that it starts performing worse
    if (cutoff < 0.0005) cutoff = 0.0005;
    if (cutoff > 0.9995) cutoff = 0.9995;
    cutoff *= M_PI;
    if (resonance < 0.001) resonance = 0.001;
    if (rolloff < 0.01) rolloff = 0.01;
    const Chunk &sig_in = input[InputSockets::input][i];
    Chunk &sig_out = output[i];
    Filter &o_filter = bundles[i];
    if (o_filter.equivalent(mode, poles, cutoff, resonance, rolloff)) {
      // Parameters haven't changed
      o_filter.process(sig_in, sig_out, false);
      continue;
    }
    Filter n_filter(mode, poles, cutoff, resonance, rolloff);
    n_filter.copy_state(o_filter);
    n_filter.process(sig_in, sig_out, o_filter.initialized);
    o_filter = n_filter;
  }
}
