from __future__ import absolute_import, division, print_function, unicode_literals

from gratipay.testing import BrowserHarness


class Tests(BrowserHarness):

    def fetch(self):
        return self.db.one('SELECT pfos.*::payments_for_open_source '
                           'FROM payments_for_open_source pfos')


    def fill_cc(self, credit_card_number, expiration, cvv):
        if self.app.env.braintree_mode == 'offline':
            self.wait_for('#braintree-container input')  # should already have fake-valid-nonce
        else:
            self.wait_for('.braintree-form-number')
            with self.get_iframe('braintree-hosted-field-number') as iframe:
                iframe.fill('credit-card-number', credit_card_number)
            with self.get_iframe('braintree-hosted-field-expirationDate') as iframe:
                iframe.fill('expiration', expiration)
            with self.get_iframe('braintree-hosted-field-cvv') as iframe:
                iframe.fill('cvv', cvv)


    def fill_form(self, amount, credit_card_number, expiration, cvv,
                  name='', email_address='',
                  promotion_name='', promotion_url='', promotion_twitter='', promotion_message=''):
        self.fill('amount', amount)
        self.fill_cc(credit_card_number, expiration, cvv)
        if name: self.fill('name', name)
        if email_address: self.fill('email_address', email_address)
        if promotion_name: self.fill('promotion_name', promotion_name)
        if promotion_url: self.fill('promotion_url', promotion_url)
        if promotion_twitter: self.fill('promotion_twitter', promotion_twitter)
        if promotion_message: self.fill('promotion_message', promotion_message)


    def test_loads_for_anon(self):
        assert self.css('#banner h1').html == 'Pay for open source.'
        assert self.css('#header .sign-in button').html.strip()[:17] == 'Sign in / Sign up'

    def test_redirects_for_authed_exclamation_point(self):
        self.make_participant('alice', claimed_time='now')
        self.sign_in('alice')
        self.reload()
        assert self.css('#banner h1').html == 'Browse'
        assert self.css('.you-are a').html.strip()[:6] == '~alice'

    def submit_succeeds(self):
        self.css('fieldset.submit button').click()
        self.wait_for('.payment-complete', 4)
        told_them = self.css('.payment-complete .description').text.startswith('Payment complete!')
        return self.fetch().succeeded and told_them

    def test_anon_can_post(self):
        self.fill_form('537', '4242424242424242', '1020', '123', 'Alice Liddell',
                       'alice@example.com', 'Wonderland', 'http://www.example.com/',
                       'thebestbutter', 'Love me! Love me! Say that you love me!')
        assert self.submit_succeeds()

    def test_optional_are_optional(self):
        self.fill_form('537', '4242424242424242', '1020', '123')
        assert self.submit_succeeds()
