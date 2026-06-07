test = {
  'name': 'Question 9',
  'points': 1,
  'suites': [
    {
      'cases': [
        {
          'code': r"""
          >>> type(light_meals) == Table
          True
          >>> light_meals.num_rows
          14
          >>> abs(avg_protein_light - 22.6) < 0.1
          True
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
