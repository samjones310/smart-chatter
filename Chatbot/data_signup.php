<?php
    $img = $_POST['image'];
    $name = $_POST['name'];
    $uid= $_POST['uid'];
    $email=$_POST['mail'];
    $password=$_POST['password'];
    $repass=$_POST['reenter'];
    $dob=$_POST['dob'];
    $org=$_POST['organisation'];
    $folderPath = "C:\\Users\\Sam Jones\\Desktop\\Chatbot_Project\\flaskr\\static\\login\\";
    $image_parts = explode(";base64,", $img);
    $image_type_aux = explode("image/", $image_parts[0]);
    $image_type = $image_type_aux[1];
    $image_base64 = base64_decode($image_parts[1]);
    $fileName = uniqid() . '.png';
    $file = $folderPath . $fileName;
    file_put_contents($file, $image_base64);
    $folderPath = "";
    $file = $folderPath . $fileName;
    file_put_contents($file, $image_base64);
    header("Location: http://localhost:5000/signup_face_temp?img_name="
    .$fileName.'&uid='.$uid.'&name='.$name.'&email='.$email.'&password='.$password.
    '&repass='.$repass.'&dob='.$dob.'&org='.$org); 
?>