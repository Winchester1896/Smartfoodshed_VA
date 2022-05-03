import axios from 'axios'


async function loadMapInitialData(){
    const path = "http://127.0.0.1:5000/g"
    const responseData = getRequest(path, {
        "204": "No content retrieved for initializing map", 
        "400": "Error in initializing map"
    })
    
    return responseData
}


async function queryMapInfoWithNode(node_list){
    const path = "http://127.0.0.1:5000/getCountyInfo" 
    const data = {
        "node": node_list
    }
    const responseData = postRequest(path, data, {
        "204": "No content retrieved for selected node list", 
        "400": "Error in retrieve geo info for the selected nodes "
    }) 
    return responseData 
}

async function postRequest(url, data, warningMsg) { 
    const response = await axios.post(url, data)
    const statusCode = response.status
    console.log(statusCode)
    if (statusCode == "204") {
        alert(warningMsg['204'])
        return null
    } else  if(statusCode == "400"){
        alert(warningMsg['400'])
        return null
    } else {
        return response['data'] 
    }
}

async function getRequest(url, warningMsg) { 
    const response = await axios.get(url)
    const statusCode = response.status
    if (statusCode == "200") {
        return response['data'] 
    } else if (statusCode == "204") {
        alert(warningMsg['204'])
        return null
    } else {
        alert(warningMsg['400'])
        return null
    } 
}

async function getNode(id){
    const path = "http://127.0.0.1:5000/countyToNodes"
    const data = {
        'county_id': id
    }
    const response = await axios.post(path, data)
    return response 
}

export {loadMapInitialData, queryMapInfoWithNode,getNode}