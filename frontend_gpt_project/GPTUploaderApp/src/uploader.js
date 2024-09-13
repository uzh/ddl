import { createApp } from 'vue'
import GPTUApp from './GPTUploaderApp.vue'
import { createI18n } from 'vue-i18n'

const i18n = new createI18n({
    fallbackLocale: 'en',
})

const selector = "#gptuapp";
const mountEl = document.querySelector(selector);
const app = createApp(GPTUApp, {...mountEl.dataset})

app.use(i18n)
app.mount(selector)
