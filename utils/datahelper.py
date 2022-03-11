import jieba


class DataClean():

    def __init__(self):
        fp = open("./data/stopwords.txt", "r", encoding="utf8")
        words = fp.readlines()
        self.stop_words = [sw.strip() for sw in words]
        fp.close()

    def clean(self, text):
        # text = self.convert_to_unicode(text)
        text = self._clean_text(text)
        words = self.jieba_cut(text)
        word_list = []
        for word in words:
            if self._is_stop_words(word) is False:
                word_list.append(word)
        return word_list

    def convert_to_unicode(self, text):
        return text.encode('utf-8').decode("unicode_escape")

    def _clean_text(self, text):
        """去除一些无意义的字符以及whitespace"""
        output = []
        for char in text:
            cp = ord(char)
            if cp == 0 or cp == 0xfffd :
                continue
            if self._is_whitespace(char):
                output.append(" ")
            else:
                output.append(char)
        return "".join(output)

    def _is_whitespace(self, char):
        """Checks whether `chars` is a whitespace character."""
        # \t, \n, and \r are technically contorl characters but we treat them
        # as whitespace since they are generally considered as such.
        if char == " " or char == "\t" or char == "\n" or char == "\r":
            return True
        return False

    def _is_stop_words(self, word):
        if word in self.stop_words:
            return True
        return False

    def jieba_cut(self, text):
        return list(jieba.cut(text))


dataclean = DataClean()
