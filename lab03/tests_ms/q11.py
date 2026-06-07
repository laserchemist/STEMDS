test = {
  'name': 'Question 11',
  'points': 1,
  'suites': [
    {
      'cases': [
        {
          'code': r"""
          >>> type(mega_sellers) == tables.Table
          True
          >>> mega_sellers.num_rows == 2
          True
          >>> list(mega_sellers.sort(0).column(0))
          ['GTA V', 'Minecraft']
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
