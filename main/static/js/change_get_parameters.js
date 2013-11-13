/**
 * http://stackoverflow.com/a/10997390/11236
 */
function updateURLParameter(url, param, paramVal){
    var newAdditionalURL = "";
    var tempArray = url.split("?");
    var baseURL = tempArray[0];
    var additionalURL = tempArray[1];
    var temp = "";
    if (additionalURL) {
        tempArray = additionalURL.split("&");
        for (var i=0; i<tempArray.length; i++){
            var parameter = tempArray[i].split('=')[0];
            parameter = decodeURIComponent(parameter);
            if(parameter != param){
                newAdditionalURL += temp + tempArray[i];
                temp = "&";
            }
        }
    }

    var rows_txt = temp + "" + param + "=" + paramVal;
    if (paramVal != undefined)
        return baseURL + "?" + newAdditionalURL + rows_txt;
    if (newAdditionalURL)
        return baseURL + "?" + newAdditionalURL;
    return baseURL
}
