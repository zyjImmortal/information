var isPro = process.env.NODE_ENV === 'production'

module.exports = {
    baseUrl: isPro ? 'http:www.zhonghemingheng.com' : '/apis'
}