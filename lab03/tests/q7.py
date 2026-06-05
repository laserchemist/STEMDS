test = {
  'name': 'Question 7',
  'points': 1,
  'suites': [
    {
      'cases': [
        {
          'code': r"""
          >>> type(renewables_sorted) == tables.Table
          True
          >>> list(renewables_sorted.column('Country').take(range(3)))
          ['Iceland', 'Bhutan', 'Paraguay']
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
