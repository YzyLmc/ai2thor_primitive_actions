; no need to make preconditions match in simulation, since those can be specified in this pddl file only

(define (domain robo-home)
    (:requirements :strips :typing :existential-preconditions :negative-preconditions :conditional-effects)

    (:types

        Robot
        Cabinet Drawer CounterTop StoveBurner Shelf Sink Fridge Toaster CoffeeMachine Faucet Microwave - location
        Knife Bottle DishSponge Egg Mug Bread Potato - item
        Drawer Cabinet Fridge Microwave - openable
        Toaster CoffeeMachine - container
        Cabinet Drawer CounterTop StoveBurner Shelf Sink - receptacle
        Toaster CoffeeMachine Faucet StoveBurner Microwave - toggleable
        Egg Mug - crackable
        Mug - dirtyable
        Bread Potato - sliceable
        Mug - pourable

    )
    (:predicates
        ; tracking cookable separately since there are prerequisites for egg and bread
        (is-cookable ?i - item)
        (at-location ?r - robot ?l - location)
        (item-on ?i - item ?r - receptacle)
        (item-in ?i - item ?l - location)
        (is-open ?o - openable)
        (is-sliced ?s - sliceable)
        (is-cooked ?i - item)
        (is-full ?p - pourable)
        (is-cracked ?c - crackable)
        (is-clean ?d - dirtyable)
        (is-on ?t - toggleable)
        (is-occupied ?c - container) ; not used now
        (omelet-made ?r - robot)
        (coffee-made ?c - CoffeeMachine)
        (breakfast ?r)
    )

    (:action move
        :parameters (?r - robot ?to - location)
        :precondition (not (at-location ?r ?to))
        :effect (and (forall
                (?l - location)
                (not (at-location ?r ?l))
            )
            (at-location ?r ?to)
        )
    )

    (:action open-openable
        :parameters (?r - robot ?o - openable)
        :precondition (and (not (is-open ?o))
            (at-location ?r ?o)
        )
        :effect (is-open ?o)
    )

    (:action pick-n-place-in-openable
        :parameters (?r - robot ?i - item ?o - openable)
        :precondition (and
            (forall
                (?j - openable)
                (not (and (not (is-open ?j)) (item-in ?i ?j)))
            )
            (is-open ?o)
        )
        :effect (and
            (forall
                (?l - openable)
                (and
                    (not (item-in ?i ?l))
                    (not (at-location ?r ?l))
                )
            )
            (forall
                (?re - receptacle)
                (and
                    (not (item-on ?i ?re))
                )
            )
            (item-in ?i ?o)
            (at-location ?r ?o)
        )
    )

    (:action pick-n-place-on-receptacle
        :parameters (?r - robot ?i - item ?re - receptacle)
        :precondition (and
            (forall
                (?j - openable)
                (not (and (not (is-open ?j)) (item-in ?i ?j)))
            )
            (not (item-on ?i ?re))
        )
        :effect (and
            (forall
                (?l - location)
                (and
                    (not (at-location ?r ?l))
                )
            )
            (forall
                (?l - location)
                (and
                    (not (item-in ?i ?l))
                )
            )
            (forall
                (?rec - receptacle)
                (and
                    (not (item-on ?i ?rec))
                )
            )
            (item-on ?i ?re)
            (at-location ?r ?re)
        )
    )

    (:action pick-n-place-in-container
        :parameters (?r - robot ?i - item ?c - container)
        :precondition (and
            (forall
                (?j - openable)
                (not (and (not (is-open ?j)) (item-in ?i ?j)))
            )
            (not (item-in ?i ?c))
            (not (is-occupied ?c))
        )
        :effect (and
            (forall
                    (?l - location)
                    (and
                        (not (at-location ?r ?l))
                    )
                )
            (forall
                (?l - location)
                (and
                    (not (item-in ?i ?l))
                )
            )
            (forall
                (?re - receptacle)
                (and
                    (not (item-on ?i ?re))
                )
            )
            (item-in ?i ?c)
            (at-location ?r ?c)
            (is-occupied ?c)
        )
    )

    ; currently doesn't bring bread to kitchen counter
    ; can add coffee to precond to make it even harder
    (:action make-breakfast
        :parameters (?k - CounterTop ?r - robot ?b - Bread)
        :precondition (and
            (is-cooked ?b)
            (item-on ?b ?k)
            (at-location ?r ?k)
        )
        :effect (breakfast ?r)
    )

    (:action toast-bread-sliced
        :parameters (?r - robot ?b - Bread ?t - Toaster)
        :precondition (and
            (at-location ?r ?t)
            (item-in ?b ?t)
            (is-sliced ?b)
            (is-on ?t)
        )
        :effect (is-cooked ?b)
    )

    (:action turn-on
        :parameters (?r - robot ?t - toggleable)
        :precondition (and
            (at-location ?r ?t)
            (not (is-on ?t))
        )
        :effect (is-on ?t)
    )

    (:action clean-in-sink
        :parameters (?r - robot ?s - sink ?d - dirtyable ?ds - DishSponge ?f - Faucet)
        :precondition (and
            (at-location ?r ?s)
            (item-on ?ds ?s)
            (item-on ?d ?s)
            (is-on ?f)
            (not (is-clean ?d))
        )
        :effect (is-clean ?d)
    )

    (:action make-coffee
        :parameters (?r - robot ?c - CoffeeMachine ?m - Mug)
        :precondition (and
            (at-location ?r ?c)
            (item-in ?m ?c)
            (not (coffee-made ?c))
            (is-clean ?m)
            (not (is-full ?m))
            (is-on ?c)
        )
        :effect (coffee-made ?c)
    )


    (:action empty-liquid
        :parameters (?r - robot ?i - pourable ?s - sink)
        :precondition (and
        (at-location ?r ?s)
        (item-on ?i ?s)
        (is-full ?i)
        )
        :effect (not (is-full ?i))
    )

    ; general slicing
    (:action slice
        :parameters (?r - robot ?s - sliceable ?t - CounterTop ?k - Knife)
        :precondition (and
            (at-location ?r ?t)
            (item-on ?s ?t)
            (item-on ?k ?t)
            (not (is-sliced ?s))
        )
        :effect (is-sliced ?s)
    )

    ; add precondition so only one thing cooked at a time?
    (:action cook-potato
        :parameters (?r - robot ?po - Potato ?s - StoveBurner)
        :precondition (and
            (at-location ?r ?s)
            (item-on ?po ?s)
            (is-sliced ?po)
            (is-on ?s)
        )
        :effect (is-cooked ?po)
    )

    (:action crack-egg
        :parameters (?r - robot ?e - Egg ?s - StoveBurner)
        :precondition (and
            (at-location ?r ?s)
            (item-on ?e ?s)
            (not (is-cracked ?e))
        )
        :effect (is-cracked ?e)
    )

    (:action cook-egg
        :parameters (?r - robot ?e - Egg ?s - StoveBurner)
        :precondition (and
            (at-location ?r ?s)
            (item-on ?e ?s)
            (is-cracked ?e)
            (is-on ?s)
            (not (is-cooked ?e))
        )
        :effect (is-cooked ?e)
    )

    (:action omelet-at-counter
        :parameters (?r - robot ?e - Egg ?k - CounterTop ?po - Potato ?b - bread)
        :precondition (and
            (at-location ?r ?k)
            (item-on ?e ?k)
            (item-on ?po ?k)
            (item-on ?b ?k)
            (is-cracked ?e)
            (is-cooked ?e)
            (is-sliced ?po)
            (is-cooked ?po)
            (is-sliced ?b)
            (is-cooked ?b)
            (not (omelet-made ?r))

        )
        :effect (omelet-made ?r)
    )
)