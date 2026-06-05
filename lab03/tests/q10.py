test = {
  'name': 'Question 10',
  'points': 1,
  'suites': [
    {
      'cases': [
        {
          'code': r"""
          >>> pop_tracks.num_rows == 29
          True
          >>> pop_tracks.sort(0).take(range(5))
          Track           | Artist          | Streams (millions) | Genre | BPM  | Energy | Danceability
          About Damn Time | Lizzo           | 1128               | Pop   | 110  | 85     | 80
          Anti-Hero       | Taylor Swift    | 1546               | Pop   | 97   | 64     | 66
          Arcade          | Duncan Laurence | 1010               | Pop   | 130  | 44     | 51
          As It Was       | Harry Styles    | 2459               | Pop   | 174  | 73     | 82
          Bam Bam         | Camila Cabello  | 913                | Pop   | 100  | 72     | 83
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
