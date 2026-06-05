test = {
  'name': 'Question 17',
  'points': 1,
  'suites': [
    {
      'cases': [
        {
          'code': r"""
          >>> sorted(city_locations.labels)
          ['City', 'Region', 'State']
          >>> city_locations.num_rows == 29
          True
          >>> city_locations.sort(0).take(range(5))
          City      | State          | Region
          Austin    | Texas          | South
          Baltimore | Maryland       | Northeast
          Boston    | Massachusetts  | Northeast
          Charlotte | North Carolina | South
          Chicago   | Illinois       | Midwest
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
