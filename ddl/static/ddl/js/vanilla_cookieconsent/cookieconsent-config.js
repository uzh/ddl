/**
 * All config. options available here:
 * https://cookieconsent.orestbida.com/reference/configuration-reference.html
 */
CookieConsent.run({

  cookie: {
    name: '_cookie_consent',
  },

  guiOptions: {
    consentModal: {
      layout: 'cloud inline',
      position: 'bottom center',
      equalWeightButtons: true,
      flipButtons: false
    },
    preferencesModal: {
      layout: 'box',
      equalWeightButtons: true,
      flipButtons: false
    }
  },

  categories: {
    necessary: {
      enabled: true,
      readOnly: true
    },
  },

  language: {
    default: 'en',
    translations: {
      en: {
        consentModal: {
          title: 'Cookie Policy',
          description: 'We only use cookies that are strictly necessary for this website to function. We do not use any tracking or advertising cookies.',
          acceptAllBtn: 'got it',
          // acceptNecessaryBtn: 'Reject all',
          showPreferencesBtn: 'learn more',
          // closeIconLabel: 'Reject all and close modal',
          footer: ``,
        },
        preferencesModal: {
          title: 'Cookie Information',
          acceptNecessaryBtn: 'Got it',
          closeIconLabel: 'Close',
          serviceCounterLabel: 'Service|Services',
          sections: [
            {
              title: 'How this website uses cookies',
              description: `This website uses only strictly necessary cookies, which are required for basic functions such as keeping you logged in and ensuring security. We do not use cookies for advertising or tracking.`,
            },
            {
              title: 'Essential functionality',
              description: 'The following cookies are required to ensure the website functions properly: ',
              linkedCategory: 'necessary',
              cookieTable: {
                headers: {
                  name: 'Cookie',
                  domain: 'Domain',
                  desc: 'Description'
                },
                body: [
                  {
                    name: 'sessionid',
                    domain: location.hostname,
                    desc: 'This cookie is created when you log in on this page. It manages your session on the website. It enables features such as logging in and accessing personal areas. Without this cookie, you would not be able to log in securely or use your settings and content on the website. It does not store any personal data and is used solely for session management. ',
                  },
                  {
                    name: 'csrftoken',
                    domain: location.hostname,
                    desc: 'This cookie protects the security of your account and your data by ensuring that only authorised actions can be carried out by your browser on this website. It helps to prevent so-called cross-site request forgery attacks. Without this cookie, malicious websites could attempt to carry out actions on your behalf without your consent. It is therefore essential for the website to function properly.',
                  },
                  {
                    name: '_cookie_consent',
                    domain: location.hostname,
                    desc: 'This cookie stores your choices regarding the use of cookies on this website. It ensures that your preferences are taken into account the next time you visit, so you do not have to set your cookie preferences again each time. Without this cookie, the website would be unable to save your cookie preferences, which would result in repeated prompts.'
                  }
                ]
              }
            },
          ]
        }
      }
    }
  }
});
