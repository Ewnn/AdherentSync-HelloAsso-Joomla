<?php
    $scriptPython = 'ajt_adherents.py';
    $output = shell_exec('python3 ' . $scriptPython);
    echo $output;
?>
