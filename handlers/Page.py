import models
from proto import Handler


class PageHandler(Handler):  # For /page/{pagenumber}
    def get(self, pagenumber):
        pagenumber = int(pagenumber)
        start = pagenumber*20 - 20
        end = start + 21
        posts = models.Post.all().order('-created')
        if self.user:
            self.render('page.html', posts=posts[start:end], user=self.user,
                        pagenumber=pagenumber)
        else:
            self.render('page.html', posts=posts[start:end],
                        pagenumber=pagenumber)
