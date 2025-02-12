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
        shelf - Shelf
        fridge - Fridge
        bread - Bread
        potato - Potato
        egg - Egg
        mug - Mug
        ; plate - Plate
        knife - Knife
        faucet - Faucet
    )
    
    (:init
        (at-location robot1 counter)
        (item-in bread cabinet)
        (item-in potato fridge)
        (item-in egg fridge)
        (item-on mug shelf)
        (item-on knife sink)
        (item-in sponge drawer)
        (not (is-clean mug))
        (is-full mug)
        (not (is-open fridge))
        (not (is-open cabinet))
        (not (is-open drawer))
        (not (is-on toaster))
        (not (is-on coffeeMachine))
        (not (is-on stoveBurner))
    )
    
    (:goal
        (and
            ; (breakfast robot1)
            (coffee-made coffeeMachine)
            (omelet-made robot1)
        )
    )
)
