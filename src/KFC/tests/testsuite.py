import unittest
import HtmlTestRunner
from xmlrunner import xmlrunner
from loginpage.loginpage_test import LoginPageTest
from profilepage.profilepage_test import ProfilePageTest
from orderpage.order_shop_test import OrderTest
# get all tests from SearchProductTest and HomePageTest class
loginpage_test = unittest.TestLoader().loadTestsFromTestCase(LoginPageTest)
profilepage_test = unittest.TestLoader().loadTestsFromTestCase(ProfilePageTest)
orderpage_test = unittest.TestLoader().loadTestsFromTestCase(OrderTest)
# create a test suite combining search_test and home_page_test
smoke_tests = unittest.TestSuite([loginpage_test,profilepage_test,orderpage_test])
# run the suite
runner = HtmlTestRunner.HTMLTestRunner(output='src/KFC/Reports',combine_reports=True,report_title='Test Report',descriptions='Smoke Tests')
#runner = xmlrunner.XMLTestRunner(verbosity=2, output='test-reports')
# run the suite using HTMLTestRunner
runner.run(smoke_tests)