test = {
  'name': 'Question 17',
  'points': 1,
  'suites': [
    {
      'cases': [
        {
          'code': r"""
          >>> sorted(parks_no_type.labels)
          ['Annual_Visitors_M', 'Country', 'Opened', 'Park']
          >>> parks_no_type.num_columns == 4
          True
          >>> parks_no_type.sort(3).take(np.arange(3))
          Park                        | Country | Annual_Visitors_M | Opened
          Tivoli Gardens              | Denmark | 4.5               | 1843
          Universal Studios Hollywood | USA     | 9.1               | 1964
          Phantasialand               | Germany | 2.5               | 1967
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
