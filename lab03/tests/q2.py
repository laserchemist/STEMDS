test = {
  'name': 'Question 2',
  'points': 1,
  'suites': [
    {
      'cases': [
        {
          'code': r"""
          >>> type(renewables) == tables.Table
          True
          >>> renewables.select('Country', 'Renewable %').sort('Country')
          Country    | Renewable %
          Albania    | 97.2
          Bhutan     | 99.9
          Costa Rica | 99.2
          Ethiopia   | 97
          Iceland    | 99.9
          Nepal      | 98.2
          Norway     | 98.5
          Paraguay   | 99.7
          Tajikistan | 98.5
          Zambia     | 84.7
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
