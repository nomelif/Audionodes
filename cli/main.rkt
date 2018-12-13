#lang racket

(require ffi/unsafe
         ffi/unsafe/define)

(define-namespace-anchor a)
(define ns (namespace-anchor->namespace a))

(define-ffi-definer define-anode (ffi-lib "../libnative"))

(define _update-state-pointer (_cpointer 'void))

(define-anode audionodes_initialize (_fun -> _void))
(define-anode audionodes_cleanup (_fun -> _void))
(define-anode audionodes_create_node (_fun _string -> _int))
(define-anode audionodes_copy_node (_fun _int _string -> _int))
(define-anode audionodes_remove_node (_fun _int -> _int))
(define-anode audionodes_update_node_input_value (_fun _int _int _float -> _void))
(define-anode audionodes_update_node_property_value (_fun _int _int _int -> _void))
(define-anode audionodes_begin_tree_update (_fun -> _update-state-pointer))
(define-anode audionodes_add_tree_update_link (_fun _update-state-pointer _int _int _size _size -> _void))
(define-anode audionodes_finish_tree_update (_fun _update-state-pointer -> _void))

(define anode-id-lookup (make-hasheq))
(define anode-type-lookup (make-hasheq))
(define anode-property-lookup (make-hasheq))
(define anode-value-lookup (make-hasheq))

(define anode-link-alist '())

(define (anode-delete-links-by-origin origin-id origin-socket)
  (begin
    (set! anode-link-alist (filter (lambda (link)
                                     (not (and
                                      (equal? (caadr link) origin-id)
                                      (equal? (cadadr link) origin-socket))))
                                   anode-link-alist))
    (anode-update-links)))


(define (anode-delete-link-by-target target-id target-socket)
  (begin
    (set! anode-link-alist (filter (lambda (link)
                                     (not (and
                                      (equal? (caadr link) target-id)
                                      (equal? (cadadr link) target-socket))))
                                   anode-link-alist))
    (anode-update-links)))

(define (anode-disconnect-node target-id)
  (begin
    (set! anode-link-alist (filter (lambda (link)
                                    (match link
                                      [(list _ (list target-id _))
                                       false]
                                      [(list (list target-id _) _)
                                       false]
                                      [_ true]))
                                  anode-link-alist))
    (anode-update-links)))

(define (anode-add-link origin-id origin-socket target-id target-socket)
  (cond
    ((not (hash-has-key? anode-id-lookup origin-id))
     (error "Can't create link from inexistent node" origin-id))
    ((not (hash-has-key? anode-id-lookup target-id))
     (error "Can't create link to inexistent node" target-id))
    (else
     (begin
      (anode-delete-link-by-target target-id target-socket)
      (set! anode-link-alist (cons (list (list origin-id origin-socket) (list target-id target-socket)) anode-link-alist))
      (anode-update-links)))))

(define (anode-update-links)
  (let
      ((ref (audionodes_begin_tree_update)))
    (begin
      (map (lambda (link)
             (match link
               [(list (list origin-id origin-socket) (list target-id target-socket))
                (audionodes_add_tree_update_link ref (hash-ref anode-id-lookup origin-id) (hash-ref anode-id-lookup target-id) origin-socket target-socket)]))
           anode-link-alist)
      (audionodes_finish_tree_update ref))))

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
                 (hash-set! anode-property-lookup node-id (make-hasheq))
                 (hash-set! anode-value-lookup node-id (make-hasheq))
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
               (hash-set! anode-property-lookup new-id (hash-ref anode-property-lookup old-id))
               (hash-set! anode-value-lookup new-id (hash-ref anode-value-lookup old-id))
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
       (anode-disconnect-node node-id)
       (audionodes_remove_node (hash-ref anode-id-lookup node-id))
       (hash-remove! anode-property-lookup node-id)
       (hash-remove! anode-value-lookup node-id)
       (hash-remove! anode-type-lookup node-id)
       (hash-remove! anode-id-lookup node-id)))
    (else
     (error "Can't delete inexistent node" node-id))))

(define (anode-node-exists node-id)
  (hash-has-key? anode-id-lookup node-id))

(define (anode-update-node-input-value node-id socket-id value)
  (cond
    ((hash-has-key? anode-id-lookup node-id)
     (begin
       (hash-set! (hash-ref anode-property-lookup node-id) socket-id value)
       (audionodes_update_node_input_value (hash-ref anode-id-lookup node-id)  socket-id value)))
    (else
     (error "Can't update input value on inexistent node" node-id))))

(define (anode-update-node-property-value node-id socket-id value)
  (cond
    ((hash-has-key? anode-id-lookup node-id)
     (begin
       (hash-set! (hash-ref anode-value-lookup node-id) socket-id value)
       (audionodes_update_node_property_value (hash-ref anode-id-lookup node-id) socket-id value)))
    (else
     (error "Can't update property value on inexistent node" node-id))))

(define (anode-update-node-binary-data node-id slot data)
  (error "TODO"))

(define (begin-tree-update) '())

(define (add-tree-update-link ref from-node to-node from-socket to-socket) '())

(define (finish-tree-update ref) '())

(define (anode-serialise-node node-id)
  (cond
    ((not (hash-has-key? anode-id-lookup node-id))
     (error "Can't serialise inexistent node" node-id))
    (else
     (list node-id (hash-ref anode-type-lookup node-id)
      (list 'inputs
            (hash->list (hash-ref anode-value-lookup node-id))
            )
      (list 'properties
            (hash->list (hash-ref anode-property-lookup node-id))
            )
      ))))

(define (anode-deserialise-nodes nodes)
  (begin
    (map
      (lambda (node-data)
        (match node-data
          [`(,node-id ,node-type ,_ ,_)
           (anode-create-node node-type node-id)
           ]
          [_
           (error "Malformed node" node-data)]))
      nodes)
    (map
      (lambda (node-data)
        (match node-data
          [`(,node-id ,_ (inputs ,input-hash) (properties ,property-hash))
           (begin
             (map (lambda (input)
                    (match input
                      [`(,socket . (,source-id ,source-socket))
                       (anode-add-link source-id source-socket node-id socket)
                       ]
                      [`(,socket . ,value)
                       (anode-update-node-input-value node-id socket value)
                       ]
                      [_
                       (error "Malformed input value" input)]
                    )) input-hash)
             (map (lambda (property)
                    (match property
                      [`(,socket . ,value)
                       (anode-update-node-property-value node-id socket value)
                       ]
                      [_
                       (error "Malformed property value" property)]
                    )) property-hash)
             )
           ]))
      nodes)
    void
    ))

(define (anode-loop)
  (begin
    (display "Turso> ")
    (let (
          (command (read))
          )
      (match command
        ['(exit)
         '()]
        [`(eval ,x)
         (begin
          (print
           (eval x ns))
          (display "\n")
          (anode-loop))]
        [_
         (begin
          (anode-deserialise-nodes command)
          (anode-loop))]))))

(define (anode-cli)
  (begin
    (anode-init)
    (anode-loop)
    (anode-cleanup)))

(anode-cli)