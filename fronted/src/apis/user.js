import req from './http.js'

export const REGISTER = params =>req('post','/api/users/register', params)

export const LOGIN = function(params){
    return req('post', '/api/users/login',params);
}