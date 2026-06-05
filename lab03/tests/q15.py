test = {
  'name': 'Question 15',
  'points': 1,
  'suites': [
    {
      'cases': [
        {
          'code': r"""
          >>> cities.take(range(3)).sort(0, descending=True)
          City          | State      | Population | Area_km2 | Region
          New York City | New York   | 8336817    | 783      | Northeast
          Los Angeles   | California | 3979576    | 1302     | West
          Chicago       | Illinois   | 2693976    | 606      | Midwest
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
