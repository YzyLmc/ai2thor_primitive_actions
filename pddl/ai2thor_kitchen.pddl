; no need to make preconditions match in simulation, since those can be specified in this pddl file only

(define (domain ai2thor_kitchen)
    (:requirements :equality :strips :typing :existential-preconditions :negative-preconditions :conditional-effects)

    (:types
        Robot location item - object
        Cabinet Drawer CounterTop StoveBurner Shelf Sink Fridge Toaster CoffeeMachine Faucet Microwave Pan Plate - location
        Knife Bottle DishSponge Egg Mug Bread Potato - item
        Drawer Cabinet Fridge Microwave - openable
        Toaster CoffeeMachine - container
        Cabinet CounterTop StoveBurner Shelf Sink Pan Plate - receptacle
        Toaster CoffeeMachine Faucet StoveBurner Microwave - toggleable
        Egg Mug - crackable
        Mug Bottle - dirtyable
        Bread Potato - sliceable
        Mug Bottle - pourable
		Egg Potato Bread - cookable
    )
    (:predicates
        ; tracking cookable separately since there are prerequisites for egg and bread
		(at-location ?r - object ?l - location)
        (is-closed ?o - location)
        (in-closed-container ?i - item ?l - location) ; an object is reachable if it's in a closed openable object
        (is-on ?t - toggleable)
        (is-sliced ?s - sliceable)
        (is-cooked ?i - cookable)
        (is-full ?p - pourable)
        (is-cracked ?c - crackable)
        (is-clean ?d - dirtyable)
        (omelet-made)
        (coffee-made)
        (toast-made)
        (breakfast-made)
    )

    (:action move
        :parameters (?r - Robot ?to - location)
        :precondition ()
                ; (not (at-location ?r ?to))
        :effect (and
            (forall
                (?j - location)
                (not (at-location ?r ?j))
            )
            (at-location ?r ?to)
        )
    )

    (:action open
        :parameters (?r - Robot ?o - openable)
        :precondition (and
            (at-location ?r ?o) ; the robot is at the openable
            (is-closed ?o)
        )
        :effect (and
            (not (is-closed ?o)) ; the openable is open
            ; all objects are deemed accessible and not in a closed container:
            (forall
                (?i - item)
                (not (in-closed-container ?i ?o))
            )
        )
    )

    (:action move-object
        :parameters (?r - Robot ?i - item ?l - location)
        :precondition (and
            ; the object being moved is not in a closed container (it is accessible)
            (forall
                (?j - location)
                (not (in-closed-container ?i ?j))
            )
            (not (is-closed ?l)) ; the location is not closed
        )
        :effect (and
            (forall
                (?j - location)
                (and
                    (not (at-location ?i ?j))
                    (not (at-location ?r ?j))
                )
            )
            ; the robot is now at the location with the object:
            ; (at-location ?r ?l)
            (at-location ?i ?l)
        )
    )

    (:action make-toast
        :parameters (?r - Robot ?b - Bread ?p - Plate ?c - CounterTop)
        :precondition (and
            (at-location ?r ?c) ; the robot is at the countertop
            (at-location ?p ?c) ; the plate is at the countertop
            (at-location ?b ?p) ; the bread is on the plate
            (is-cooked ?b) ; the bread is toasted
            ; (not (toast-made)) ; the toast has not been made
        )
        :effect (toast-made) ; toast has been made
    )

    (:action slice
        :parameters (?r - Robot ?s - sliceable ?t - CounterTop ?k - Knife)
        :precondition (and
            (at-location ?r ?t) ; the robot is at the countertop
            (at-location ?s ?t) ; the item is on the countertop
            (at-location ?k ?t) ; the knife is on the countertop
            ; (not (is-sliced ?s)) ; the item has not been sliced
        )
        :effect (is-sliced ?s) ; the item is sliced
    )

    (:action toast-bread
        :parameters (?r - Robot ?b - Bread ?t - Toaster)
        :precondition (and
            (at-location ?r ?t) ; the robot is at the toaster
            (at-location ?b ?t) ; the bread is in the toaster
            (is-sliced ?b) ; the bread is sliced
            (is-on ?t) ; the toaster is on
        )
        :effect (is-cooked ?b) ; the bread is cooked (toasted)
    )

    (:action turn-on
        :parameters (?r - Robot ?t - toggleable)
        :precondition (and
            (at-location ?r ?t) ; the robot is at the toggleable object
            ; (not (is-on ?t)) ; the object is not on
        )
        :effect (is-on ?t) ; the object is now turned on
    )

    (:action clean
        :parameters (?r - Robot ?d - dirtyable ?s - sink ?ds - DishSponge ?f - Faucet)
        :precondition (and
            (at-location ?r ?s) ; the robot is at the sink
            (at-location ?d ?s) ; the dirty object is at the sink
            (at-location ?ds ?s) ; the sponge is at the sink
            (is-on ?f) ; the faucet is on
            ; (not (is-clean ?d)) ; the dirty object is not clean
        )
        :effect (is-clean ?d) ; the dirty object is clean
    )

    (:action make-coffee
        :parameters (?r - Robot ?c - CoffeeMachine ?m - Mug)
        :precondition (and
            (at-location ?r ?c) ; the robot is at the coffee machine
            (at-location ?m ?c) ; the mug is in the coffee machine
            ; (not (coffee-made)) ; coffee has not been made
            (is-clean ?m) ; the mug is clean
            (not (is-full ?m)) ; the mug is not full
            (is-on ?c) ; the coffee machine is on
        )
        :effect (coffee-made) ; coffee has been made
    )

    (:action empty-liquid
        :parameters (?r - Robot ?i - pourable ?s - Sink)
        :precondition (and
            (at-location ?r ?s) ; the robot is at the sink
            (at-location ?i ?s) ; the item is at the sink
            (is-full ?i) ; the item is full
        )
        :effect (and
            (not (is-full ?i)) 
            (not (is-clean ?i))  ; the item is not full and clean
        )
    )

    (:action cook-potato
        :parameters (?r - Robot ?po - Potato ?p - Pan ?s - StoveBurner)
        :precondition (and
            (at-location ?r ?s) ; the robot is at the stove
            (at-location ?p ?s) ; the pan is on the stove
            (at-location ?po ?p) ; the potato is on the pan
            (is-sliced ?po) ; the potato is sliced
            (is-on ?s) ; the stove is turned on
            ; (not (is-cooked ?p)) ; the potato is not cooked
        )
        :effect (is-cooked ?po) ; the potato is cooked
    )

    (:action crack-egg
        :parameters (?r - Robot ?e - Egg ?p - Pan ?s - StoveBurner)
        :precondition (and
            (at-location ?r ?s) ; the robot is at the stove
            (at-location ?p ?s) ; the pan is on the stove
            (at-location ?e ?p) ; the egg is at the pan
            ; (not (is-cracked ?e)) ; the egg is not cracked
        )
        :effect (is-cracked ?e) ; the egg is cracked
    )

    (:action cook-egg
        :parameters (?r - Robot ?e - Egg ?p - Pan ?s - StoveBurner)
        :precondition (and
            (at-location ?r ?s) ; the robot is at the stove
            (at-location ?p ?s) ; the pan is on the stove
            (at-location ?e ?p) ; the egg is at the pan
            (is-cracked ?e) ; the egg is cracked
            (is-on ?s) ; the stove is turned on
            ; (not (is-cooked ?e)) ; the egg is not cooked
        )
        :effect (is-cooked ?e) ; the egg is cooked
    )

    (:action make-omelet
        :parameters (?r - Robot ?e - Egg ?po - Potato ?b - bread ?p - Plate ?c - CounterTop)
        :precondition (and
            (at-location ?r ?c) ; the robot is at the countertop
            (at-location ?p ?c) ; the plate is at the countertop
            (at-location ?e ?p) ; the egg is on the plate
            (at-location ?po ?p) ; the potato is on the plate
            ; (at-location ?b ?p) ; the bread is on the plate
            (is-cooked ?e) ; the egg is cooked
            (is-cooked ?po) ; the potato is cooked
            ; (is-cooked ?b) ; the bread is toasted
            ; (not (omelet-made)) ; the omelet has not been made
        )
        :effect (omelet-made) ; the omelet has been made
    )

    (:action make-breakfast
        :parameters() ; no parameters -- this action just needs the following subtasks done
        :precondition (and
            (omelet-made) ; omelet is made
            (coffee-made) ; coffee is made
            (toast-made) ; toast is made
        )
        :effect (breakfast-made) ; full breakfast is made
    )
)