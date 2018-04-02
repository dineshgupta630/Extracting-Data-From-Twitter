import unittest
from main import youtube_url_or_not
from main import video_id


class YouTubeURLOrNot(unittest.TestCase):

    def testOne(self):
        self.assertTrue(youtube_url_or_not('http://youtu.be/SA2iWivDJiE'))
        self.assertTrue(youtube_url_or_not('http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu'))
        self.assertTrue(youtube_url_or_not('http://www.youtube.com/embed/SA2iWivDJiE'))

    def testTwo(self):
        self.assertFalse(youtube_url_or_not(2))
        self.assertFalse(youtube_url_or_not('http://www.yoeutube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US'))


class YouTubeVideoID(unittest.TestCase):

    def testOne(self):
        self.assertTrue(video_id('http://youtu.be/SA2iWivDJiE'))
        self.assertTrue(video_id('http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu'))
        self.assertTrue(video_id('http://www.youtube.com/embed/SA2iWivDJiE'))

    def testTwo(self):
        self.assertFalse(video_id('222'))
        self.assertFalse(video_id(222))
        self.assertFalse(video_id('http://www.sdyoeutube.com/fdfdsfsvs/SsddA2iWivDJiE?version=3&amp;hl=en_US'))


def main():
    unittest.main()

if __name__ == '__main__':
    main()