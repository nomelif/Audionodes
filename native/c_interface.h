void initialize();
void cleanup();
int create_node(const char*);
int copy_node(int, const char*);
void remove_node(int);
bool node_exists(int);
void update_node_input_value(int, int, float);
void update_node_property_value(int, int, int);
void* begin_tree_update();
void add_tree_update_link(void*, int, int, size_t, size_t);
void finish_tree_update(void*);

