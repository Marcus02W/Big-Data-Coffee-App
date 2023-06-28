function signup(){

    const formData = new FormData();
    var id = document.getElementById("id").value;
    var name = document.getElementById("name").value;
    var country = document.getElementById("country").value;
    var city = document.getElementById("city").value;
    var adress = document.getElementById("adress").value;
    var firstname = document.getElementById("owner_firstname").value;
    var lastname = document.getElementById("owner_lastname").value;
    var password = document.getElementById("psw").value;

    formData.append("shop_id", id);
    formData.append("name", name);
    formData.append("country", country);
    formData.append("city", city);
    formData.append("street", adress);
    formData.append("owner_firstname", firstname);
    formData.append("owner_lastname", lastname);
    formData.append("password", password);

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/signup_api_coffee_shop");
    xhr.send(formData);

    xhr.onreadystatechange = () => {
        if (xhr.readyState === 4){
            response = xhr.responseText;
            
            console.log(response);
            if (response=="failed") {
                document.getElementById("response").innerHTML="Registering failed! The user already exists or the id is invalid (has to be numerical)!"
            } 

            else{
                document.getElementById("response").innerHTML="Registration successfull! Make your excellent coffee accessible to a broad coffee loving community.."
                document.getElementById("login_link").style.display="inline";
                setTimeout(() => {
                    window.location.href = '/login_coffee_shop';
                  }, 1000);
            } 
        }
    }

}