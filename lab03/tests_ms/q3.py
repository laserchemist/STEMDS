test = {
  'name': 'Question 3',
  'points': 1,
  'suites': [
    {
      'cases': [
        {
          'code': r"""
          >>> type(lunch) == tables.Table
          True
          >>> lunch.num_rows == 20
          True
          >>> lunch.select('Meal', 'Calories', 'Protein_g', 'Carbs_g', 'Fat_g').sort(0).take(range(5))
          Meal                      | Calories | Protein_g | Carbs_g | Fat_g
          Bean Burrito              | 420      | 17        | 62      | 12
          Beef Stir Fry with Rice   | 480      | 28        | 65      | 11
          Beef Tacos (2)            | 500      | 28        | 44      | 22
          Caesar Salad with Chicken | 390      | 35        | 18      | 19
          Cheese Pizza (2 slices)   | 490      | 20        | 58      | 18
          """,
          'hidden': False,
          'locked': False
        }
      ],
      'scored': True,
      'setup': '',
      'teardown': '',
      'type': 'doctest'
    }
  ]
}
