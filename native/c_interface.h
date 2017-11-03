void initialize();
void cleanup();
int create_node(int);
int copy_node(int, int);
void remove_node(int);
void update_node_input_value(int, int, float);
void* begin_tree_update();
void add_tree_update_link(void*, int, int, size_t, size_t);
void finish_tree_update(void*);

