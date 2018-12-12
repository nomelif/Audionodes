#lang racket

(require ffi/unsafe
         ffi/unsafe/define)

(define-ffi-definer define-anode (ffi-lib "../libnative"))

(define-anode audionodes_initialize (_fun -> _void))
(define-anode audionodes_cleanup (_fun -> _void))
(define-anode audionodes_create_node (_fun _string -> _int))
(define-anode audionodes_copy_node (_fun _int _string -> _int))
(define-anode audionodes_remove_node (_fun _int -> _int))
(define-anode audionodes_update_node_input_value (_fun _int _int _float -> _void))
(define-anode audionodes_update_node_property_value (_fun _int _int _int -> _void))

(define anode-id-lookup (make-hasheq))
(define anode-type-lookup (make-hasheq))

(define (anode-init)
  (audionodes_initialize))

(define (anode-cleanup)
  (audionodes_cleanup))

(define (anode-create-node node-type node-id)
  (cond
    ((hash-has-key? anode-id-lookup node-id)
     (error "Node with id already exists:" node-id))
    (else
     (let ((numeric-id (audionodes_create_node node-type)))
       (cond
         ((equal? numeric-id -1)
          (error "Failed to create node" node-id))
         (else (begin
                 (hash-set! anode-id-lookup node-id numeric-id)
                 (hash-set! anode-type-lookup node-id node-type))))))))

(define (anode-copy-node old-id new-id)
  (cond
    ((hash-has-key? anode-id-lookup old-id)
     (cond
       ((not (hash-has-key? anode-id-lookup new-id))
        (let ((numeric-id (audionodes_copy_node (hash-ref anode-id-lookup old-id) (hash-ref anode-type-lookup old-id))))
          (cond
            ((equal? numeric-id -1)
             (error "Failed to copy" old-id))
            (else
             (begin
               (hash-set! anode-id-lookup new-id numeric-id)
               (hash-set! anode-type-lookup new-id (hash-ref anode-type-lookup old-id)))))))
       (else
        (error "A node with the ID selected for copy target already exists:" new-id))))
    (else
     (error "Can't copy inexistent node" old-id))))

(define (anode-remove-node node-id)
  (cond
    ((hash-has-key? anode-id-lookup node-id)
     (begin
       (audionodes_remove_node (hash-ref anode-id-lookup node-id))
       (hash-remove! anode-type-lookup (hash-ref anode-id-lookup node-id))
       (hash-remove! anode-id-lookup node-id)))
    (else
     (error "Can't delete inexistent node" node-id))))

(define (anode-node-exists node-id)
  (hash-has-key? anode-id-lookup node-id))

(define (anode-update-node-input-value node-id socket-id value)
  (cond
    ((hash-has-key? anode-id-lookup node-id)
     (audionodes_update_node_input_value socket-id value))
    (else
     (error "Can't update input value on inexistent node" node-id))))

(define (anode-update-node-property-value node-id socket-id value)
  (cond
    ((hash-has-key? anode-id-lookup node-id)
     (audionodes_update_node_property_value socket-id value))
    (else
     (error "Can't update property value on inexistent node" node-id))))

(define (anode-update-node-binary-data node-id slot data)
  (error "TODO"))

(define (begin-tree-update) '())

(define (add-tree-update-link ref from-node to-node from-socket to-socket) '())

(define (finish-tree-update ref) '())


