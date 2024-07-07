(define
	(problem smartbloom)
	(:domain smartbloomsystem)
	(:objects
		lt1 - lighttime
		l1 - light
		m1 - moisture
		t1 - temp
	)
	(:init (light-is-off l1) (temp-is-low t1) (moisture-is-low m1))
	(:goal (and (temp-is-ok t1) (moisture-is-ok m1)))
)
