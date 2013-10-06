from django.test import TestCase

from reviewboard.reviews.models import Comment, \
                                       DefaultReviewer, \
                                       Group, \
                                       ReviewRequest, \
                                       ReviewRequestDraft, \
                                       Review, \
                                       Screenshot
    fixtures = ['test_users', 'test_reviewrequests', 'test_scmtools',
                'test_site']
            ReviewRequest.objects.public(
                User.objects.get(username="doc")), [
            "Comments Improvements",
            "Update for cleaned_data changes",
            "Add permission checking for JSON API",
            "Made e-mail improvements",
            "Error dialog",
            "Interdiff Revision Test",
        ])
            ReviewRequest.objects.public(status=None), [
            "Update for cleaned_data changes",
            "Add permission checking for JSON API",
            "Made e-mail improvements",
            "Error dialog",
            "Improved login form",
            "Interdiff Revision Test",
        ])
            ReviewRequest.objects.public(
                User.objects.get(username="doc"), status=None), [
            "Comments Improvements",
            "Update for cleaned_data changes",
            "Add permission checking for JSON API",
            "Made e-mail improvements",
            "Error dialog",
            "Improved login form",
            "Interdiff Revision Test",
        ])
            ["Add permission checking for JSON API"])
            ["Add permission checking for JSON API"])
            ["Update for cleaned_data changes",
             "Add permission checking for JSON API"])
            ReviewRequest.objects.to_user_groups("doc", status=None,
                local_site=None),
            ["Update for cleaned_data changes",
             "Add permission checking for JSON API"])
            ReviewRequest.objects.to_user_groups("doc",
                User.objects.get(username="doc"), local_site=None),
            ["Comments Improvements",
             "Update for cleaned_data changes",
             "Add permission checking for JSON API"])
            ["Add permission checking for JSON API",
             "Made e-mail improvements"])
            ["Add permission checking for JSON API",
             "Made e-mail improvements",
             "Improved login form"])
            ReviewRequest.objects.to_user_directly("doc",
                User.objects.get(username="doc"), status=None, local_site=None),
            ["Add permission checking for JSON API",
             "Made e-mail improvements",
             "Improved login form"])
            ReviewRequest.objects.from_user("doc", local_site=None), [])
            ReviewRequest.objects.from_user("doc", status=None, local_site=None),
            ["Improved login form"])
            ReviewRequest.objects.from_user("doc",
                user=User.objects.get(username="doc"), status=None,
                local_site=None),
            ["Comments Improvements",
             "Improved login form"])
            ReviewRequest.objects.to_user("doc", local_site=None), [
            "Update for cleaned_data changes",
            "Add permission checking for JSON API",
            "Made e-mail improvements"
        ])
            ReviewRequest.objects.to_user("doc", status=None, local_site=None), [

            "Update for cleaned_data changes",
            "Add permission checking for JSON API",
            "Made e-mail improvements",
            "Improved login form"
        ])
            ReviewRequest.objects.to_user("doc",
                User.objects.get(username="doc"), status=None, local_site=None), [
            "Comments Improvements",
            "Update for cleaned_data changes",
            "Add permission checking for JSON API",
            "Made e-mail improvements",
            "Improved login form"
        ])
            self.assert_(summary in summaries,
                         u'summary "%s" not found in summary list' % summary)
            self.assert_(summary in r_summaries,
                         u'summary "%s" not found in review request list' %
                         summary)
    fixtures = ['test_users', 'test_reviewrequests', 'test_scmtools',
                'test_site']
        review_request = ReviewRequest.objects.public()[0]
        response = self.client.get('/r/3/')
        self.assertEqual(request.submitter.username, 'admin')
        self.assertEqual(request.summary, 'Add permission checking for JSON API')
        self.assertEqual(request.description,
                         'Added some user permissions checking for JSON API functions.')
        self.assertEqual(request.testing_done, 'Tested some functions.')

        self.assertEqual(request.target_people.count(), 2)
        self.assertEqual(request.target_people.all()[0].username, 'doc')
        self.assertEqual(request.target_people.all()[1].username, 'dopey')

        self.assertEqual(request.target_groups.count(), 1)
        self.assertEqual(request.target_groups.all()[0].name, 'privgroup')

        self.assertEqual(request.bugs_closed, '1234, 5678, 8765, 4321')
        self.assertEqual(request.status, 'P')

        # TODO - diff
        # TODO - reviews

        self.client.logout()
        review_request = ReviewRequest.objects.get(
            summary="Add permission checking for JSON API")
        filediff = \
            review_request.diffset_history.diffsets.latest().files.all()[0]

        # Remove all the reviews on this.
        review_request.reviews.all().delete()
        main_review = Review.objects.create(review_request=review_request,
                                            user=user1)
        main_comment = main_review.comments.create(filediff=filediff,
                                                   first_line=1,
                                                   num_lines=1,
                                                   text=comment_text_1)
        reply1 = Review.objects.create(review_request=review_request,
                                       user=user1,
                                       base_reply_to=main_review,
                                       timestamp=main_review.timestamp +
                                                 timedelta(days=1))
        reply1.comments.create(filediff=filediff,
                               first_line=1,
                               num_lines=1,
                               text=comment_text_2,
                               reply_to=main_comment)
        reply2 = Review.objects.create(review_request=review_request,
                                       user=user2,
                                       base_reply_to=main_review,
                                       timestamp=main_review.timestamp +
                                                 timedelta(days=2))
        reply2.comments.create(filediff=filediff,
                               first_line=1,
                               num_lines=1,
                               text=comment_text_3,
                               reply_to=main_comment)
        comments = entry['diff_comments']
        filename = os.path.join(settings.HTDOCS_ROOT,
                                'media', 'rb', 'images', 'trophy.png')
                                              file=file)
                                              file=file)
                                              file=file)
        comments = entry['file_attachment_comments']
        comments = entry['screenshot_comments']
        self.client.logout()

    def testNewReviewRequest1(self):
        """Testing new_review_request view (uploading diffs)"""
        self.client.login(username='grumpy', password='grumpy')

        response = self.client.get('/r/new/')
        self.assertEqual(response.status_code, 200)

        testdata_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'scmtools', 'testdata')
        svn_repo_path = os.path.join(testdata_dir, 'svn_repo')

        repository = Repository(name='Subversion SVN',
                                path='file://' + svn_repo_path,
                                tool=Tool.objects.get(name='Subversion'))
        repository.save()

        diff_filename = os.path.join(testdata_dir, 'svn_makefile.diff')

        f = open(diff_filename, 'r')

        response = self.client.post('/r/new/', {
            'repository': repository.id,
            'diff_path': f,
            'basedir': '/trunk',
        })

        f.close()

        self.assertEqual(response.status_code, 302)

        r = ReviewRequest.objects.order_by('-time_added')[0]
        self.assertEqual(response['Location'],
                         'http://testserver%s' % r.get_absolute_url())

        self.assert_(datagrid)
        self.assertEqual(len(datagrid.rows), 6)
        self.assertEqual(datagrid.rows[0]['object'].summary,
                         'Interdiff Revision Test')
        self.assertEqual(datagrid.rows[1]['object'].summary,
                         'Made e-mail improvements')
        self.assertEqual(datagrid.rows[2]['object'].summary,
                         'Improved login form')
        self.assertEqual(datagrid.rows[3]['object'].summary,
                         'Error dialog')
        self.assertEqual(datagrid.rows[4]['object'].summary,
                         'Update for cleaned_data changes')
        self.assertEqual(datagrid.rows[5]['object'].summary,
                         'Add permission checking for JSON API')

        self.client.logout()
        self.assert_(datagrid)
        self.assert_(datagrid)
        self.assert_(datagrid)
        self.assertEqual(len(datagrid.rows), 4)
        self.assertEqual(datagrid.rows[0]['object'].summary,
                         'Made e-mail improvements')
        self.assertEqual(datagrid.rows[1]['object'].summary,
                         'Update for cleaned_data changes')
        self.assertEqual(datagrid.rows[2]['object'].summary,
                         'Comments Improvements')
        self.assertEqual(datagrid.rows[3]['object'].summary,
                         'Add permission checking for JSON API')

        self.client.logout()
        self.assert_(datagrid)
        self.assertEqual(datagrid.rows[0]['object'].summary,
                         'Interdiff Revision Test')
        self.assertEqual(datagrid.rows[1]['object'].summary,
                         'Add permission checking for JSON API')

        self.client.logout()
        self.assert_(datagrid)
        self.assertEqual(datagrid.rows[0]['object'].summary,
                         'Made e-mail improvements')
        self.assertEqual(datagrid.rows[1]['object'].summary,
                         'Add permission checking for JSON API')

        self.client.logout()
        self.assert_(datagrid)
        self.assertEqual(datagrid.rows[0]['object'].summary,
                         'Update for cleaned_data changes')
        self.assertEqual(datagrid.rows[1]['object'].summary,
                         'Comments Improvements')

        self.client.logout()
        """Testing dashboard view (to-group devgroup)"""
        profile = user.get_profile()
        local_site = None
        datagrid = self.getContextVar(response, 'datagrid')
        self.assertEqual(
            datagrid.counts['outgoing'],
            ReviewRequest.objects.from_user(
                user, user, local_site=local_site).count())
        self.assertEqual(
            datagrid.counts['incoming'],
            ReviewRequest.objects.to_user(user, local_site=local_site).count())
        self.assertEqual(
            datagrid.counts['to-me'],
            ReviewRequest.objects.to_user_directly(
                user, local_site=local_site).count())
        self.assertEqual(
            datagrid.counts['starred'],
            profile.starred_review_requests.public(
                user, local_site=local_site).count())
        self.assertEqual(datagrid.counts['mine'],
            ReviewRequest.objects.from_user(
                user, user, None, local_site=local_site).count())
        self.assertEqual(datagrid.counts['groups']['devgroup'],
            ReviewRequest.objects.to_group(
                'devgroup', local_site=local_site).count())
        self.assertEqual(datagrid.counts['groups']['privgroup'],
            ReviewRequest.objects.to_group(
                'privgroup', local_site=local_site).count())

        self.client.logout()
        response = self.client.get('/r/8/diff/1-2/')
        self.assertEqual(self.getContextVar(response, 'num_diffs'), 3)
        self.assert_(files)
        self.assertEqual(files[0]['depot_filename'],
                         '/trunk/reviewboard/TESTING')
        self.assert_('fragment' in files[0])
        self.assert_('interfilediff' in files[0])
        self.assertEqual(files[1]['depot_filename'],
                         '/trunk/reviewboard/settings_local.py.tmpl')
        self.assert_('fragment' not in files[1])
        self.assert_('interfilediff' in files[1])
        response = self.client.get('/r/8/diff/2-3/')
        self.assertEqual(self.getContextVar(response, 'num_diffs'), 3)
        self.assert_(files)
        self.assertEqual(files[0]['depot_filename'],
                         '/trunk/reviewboard/NEW_FILE')
        self.assert_('fragment' in files[0])
        self.assert_('interfilediff' in files[0])
        self.assert_(datagrid)
        self.assertEqual(datagrid.rows[0]['object'].summary,
                         'Improved login form')
        self.assertEqual(datagrid.rows[1]['object'].summary,
                         'Comments Improvements')

        self.client.logout()
        review_request = ReviewRequest.objects.get(
            summary="Add permission checking for JSON API")
        filediff = \
            review_request.diffset_history.diffsets.latest().files.all()[0]
        review = Review(review_request=review_request, user=user)
        review.save()

        comment = review.comments.create(filediff=filediff, first_line=1)
        comment.text = 'This is a test'
        comment.issue_opened = True
        comment.issue_status = Comment.OPEN
        comment.num_lines = 1
        comment.save()

    fixtures = ['test_users', 'test_reviewrequests', 'test_scmtools']
        self.assert_("summary" in fields)
        self.assert_("description" in fields)
        self.assert_("testing_done" in fields)
        self.assert_("branch" in fields)
        self.assert_("bugs_closed" in fields)
        return ReviewRequestDraft.create(ReviewRequest.objects.get(
            summary="Add permission checking for JSON API"))
    def testLongBugNumbers(self):
    def testNoSummary(self):
    fixtures = ['test_users', 'test_reviewrequests', 'test_scmtools']
        review_request = ReviewRequest.objects.get(
            summary="Add permission checking for JSON API")
        filediff = \
            review_request.diffset_history.diffsets.latest().files.all()[0]
        review = Review(review_request=review_request, user=user)
        review.body_top = body_top
        review.save()
        master_review = review

        comment = review.comments.create(filediff=filediff, first_line=1)
        comment.text = comment_text_1
        comment.num_lines = 1
        comment.save()
        review = Review(review_request=review_request, user=user)
        review.save()

        comment = review.comments.create(filediff=filediff, first_line=1)
        comment.text = comment_text_2
        comment.num_lines = 1
        comment.save()
        review = Review(review_request=review_request, user=user)
        review.body_bottom = body_bottom
        review.save()

        comment = review.comments.create(filediff=filediff, first_line=1)
        comment.text = comment_text_3
        comment.num_lines = 1
        comment.save()
        self.assert_(review)
    fixtures = ['test_scmtools.json']
        self.assert_(len(default_reviewers) == 2)
        self.assert_(default_reviewer1 in default_reviewers)
        self.assert_(default_reviewer2 in default_reviewers)
        self.assert_(len(default_reviewers) == 1)
        self.assert_(default_reviewer2 in default_reviewers)
        default_reviewers = DefaultReviewer.objects.for_repository(None, test_site)
        self.assert_(len(default_reviewers) == 1)
        self.assert_(default_reviewer1 in default_reviewers)
        self.assert_(len(default_reviewers) == 1)
        self.assert_(default_reviewer2 in default_reviewers)
    fixtures = ['test_scmtools.json']
    fixtures = ['test_users', 'test_reviewrequests', 'test_scmtools',
                'test_site']
        review_request = self._get_review_request()
        review_request = self._get_review_request()
        review_request = self._get_review_request()
        review_request = self._get_review_request()
        review_request.save()

        review_request = self._get_review_request()
        review_request.save()

        review_request = self._get_review_request()
        review_request.save()

    def _get_review_request(self, local_site=None):
        # Get a review request and clear out the reviewers.
        review_request = ReviewRequest.objects.public(local_site=local_site)[0]
        review_request.target_people.clear()
        review_request.target_groups.clear()
        return review_request
