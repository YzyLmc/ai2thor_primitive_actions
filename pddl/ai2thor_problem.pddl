(define (problem test)
    (:domain robo-home)
    
    (:objects
        robot1 - Robot
        counter - CounterTop
        sink - Sink
        sponge - DishSponge
        toaster - Toaster
        coffeeMachine - CoffeeMachine
        stoveBurner - StoveBurner
        cabinet - Cabinet
        drawer - Drawer
        bread - Bread
        potato - Potato
        egg - Egg
        mug - Mug
        plate - Plate
        knife - Knife
        pan - Pan
        faucet - Faucet
    )
    
    (:init
        (at-location robot1 counter)
        (item-on bread counter)
        (item-on potato counter)
        (item-on egg counter)
        (item-on mug counter)
        (item-on plate counter)
        (item-on knife counter)
        (item-on sponge counter)
        (item-on pan stoveBurner)
        (is-open cabinet)
        (is-open drawer)
        (not (is-clean mug))
        (is-clean plate)
        (is-full mug)
        (not (is-on toaster))
        (not (is-on coffeeMachine))
        (not (is-on stoveBurner))
    )
    
    (:goal
        (and
            ; (breakfast robot1)
            (is-cooked bread)
            (item-on bread plate)
            ; (coffee-made coffeeMachine)
        )
    )
)
