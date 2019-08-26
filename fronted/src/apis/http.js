import axios from 'axios'
import apiConfig from './api.config'

const instance = axios.create({
    baseUrl: apiConfig.baseUrl,
    timeout:6000
})

// 响应拦截器
instance.interceptors.response.use(function(response){
    return response.data;
}, function(error){
    return Promise.reject(error);
});

instance.interceptors.request.use(function(config){
    return config;
},function(error){
    return Promise.reject(error);
})


export default function(method,url,data=null){
    method = method.toLowerCase();
    if (method == 'post') {
        return instance.post(url,data);
    } else if(method == 'get'){
        return instance.get(url,{params:data});
    }else{
        console.log('位置的method' + method)
        return false;
    }
}


