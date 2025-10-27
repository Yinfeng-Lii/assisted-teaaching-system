<?php
// NOTE: This code is vulnerable to SQL injection. 
// It should use prepared statements (e.g., with mysqli_prepare or PDO) for security.
// The variables $servername, $username, $password, $dbname are not defined here.

$conn = new mysqli($servername, $username, $password, $dbname);
if ($conn->connect_error) { 
    die("连接失败: " . $conn->connect_error); 
}

// Attempt to create table (will fail silently if it already exists)
$sql = "CREATE TABLE users (
    id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY, 
    username VARCHAR(30) NOT NULL, 
    password VARCHAR(30) NOT NULL
)";
// mysqli_query($conn, $sql); // It's good practice to handle the return value

if(isset($_POST["register"])){
    $username = mysqli_real_escape_string($conn, $_POST['username']);
    $password = mysqli_real_escape_string($conn, $_POST['password']); // Passwords should be hashed!
    
    $check_user = "SELECT * FROM users WHERE username='$username'";
    $result = mysqli_query($conn, $check_user);
    $count = mysqli_num_rows($result);
    
    if($count == 0){
        //将新用户信息插入用户表
        $insert_user = "INSERT INTO users (username, password) VALUES ('$username', '$password')";
        mysqli_query($conn, $insert_user);
        echo "用户注册成功";
    } else {
        echo "用户名已存在,请选择其他用户名";
    }
}

if(isset($_POST["login"])){
    $username = mysqli_real_escape_string($conn, $_POST['username']);
    $password = mysqli_real_escape_string($conn, $_POST['password']);
    
    $login_user = "SELECT * FROM users WHERE username='$username' AND password='$password'";
    $result = mysqli_query($conn, $login_user);
    $count = mysqli_num_rows($result);
    
    if($count == 1){
        echo "用户登录成功";
    } else {
        echo "用户名或密码错误,请重新输入";
    }
}

$conn->close();
?>