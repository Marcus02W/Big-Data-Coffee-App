window.onload = () => {
    const formData = new FormData();
    var username = document.cookie['username'];
    var password = document.cookie['password'];
    formData.append("username", username);
    formData.append("password", password);

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/login_api");
    xhr.send(formData);

    xhr.onreadystatechange = () => {
        if (xhr.readyState === 4){
            response = xhr.responseText;
            response = JSON.parse(response);
            console.log(response);
        }
    }
}