void audionodes_initialize();
void audionodes_cleanup();
int audionodes_create_node(const char*);
int audionodes_copy_node(int, const char*);
void audionodes_remove_node(int);
bool audionodes_node_exists(int);

void audionodes_update_node_input_value(int, int, float);
void audionodes_update_node_property_value(int, int, int);
void audionodes_send_node_binary_data(int, int, int, void*);

struct AudionodesConfigurationDescriptor {
  bool field_populated;
  const char *name, *current_value;
  const char **available_values;
};
// returns a list of AudionodesConfigurationDescriptor, last item always has
// field_populated == false
AudionodesConfigurationDescriptor* audionodes_get_configuration_options(int);
int audionodes_set_configuration_option(int, const char*, const char*);

void audionodes_begin_tree_update();
void audionodes_add_tree_update_link(int, int, size_t, size_t);
void audionodes_finish_tree_update();

