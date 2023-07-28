function login(){
    
    const formData = new FormData();
    var username = document.getElementById("uname").value;
    var password = document.getElementById("psw").value;
    formData.append("username", username);
    formData.append("password", password);

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/login_api_customer");
    xhr.send(formData);

    xhr.onreadystatechange = () => {
        if (xhr.readyState === 4){
            response = xhr.responseText;
            console.log(response);
            if (response=="failed") {
                document.getElementById("response").innerHTML="Login failed! Invalid username and/or password."
            } 

            else{
                response = JSON.parse(response);

                // setting a cookie based on login credentials to verify validity of user in other pages
                document.cookie = "username="+response['username'];
                document.cookie = "password="+response['password'];
                console.log(document.cookie);
                document.getElementById("response").innerHTML="Login successfull! Explore a world full of the finest coffee."
                setTimeout(() => {
                    window.location.href = '/customer_landing';
                  }, 1000);
                
            } 
        }
    }

}