const cookieData = document.getElementById('cookie-data');
const cookiebarSrc = cookieData.dataset.cookiebarSrc;
const statusUrl = cookieData.dataset.statusUrl;

const showShareButton = () => {
    const template = document.getElementById('show-share-button')
    const showButtonScript = template.content.cloneNode(true);
    document.body.appendChild(showButtonScript);
};

async function loadCookieBar() {
  try {
    const { showCookieBar } = await import(cookiebarSrc);
    showCookieBar({
        statusUrl: statusUrl,
        templateSelector: '#cookie-consent__cookie-bar',
        cookieGroupsSelector: '#cookie-consent__cookie-groups',
        onShow: () => document.querySelector('body').classList.add('with-cookie-bar'),
        onAccept: (cookieGroups) => {
            document.querySelector('body').classList.remove('with-cookie-bar');
            const hasSocial = cookieGroups.find(g => g.varname == 'social') !== undefined;
            hasSocial && showShareButton();
        },
        onDecline: () => document.querySelector('body').classList.remove('with-cookie-bar'),
    });
  } catch (error) {
    console.error("Error loading cookie bar script:", error);
  }
}

loadCookieBar();
