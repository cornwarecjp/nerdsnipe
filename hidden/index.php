<html>
<body>
Note: there is a solution, with SHA256sum 083215477510be65f0bac53e84a531e826db4e3873f261dba2cdfc362843a37.
<p>
Your program:<br>
<form action="." method="POST">
<textarea name="program" cols=80 rows=25><?php
echo $_POST["program"];
?></textarea><br>
<input name="submit" type="submit" value="Submit">
</form>
<?php
function runProgram()
{
	$wouldBlock = false;
	$lockfp = fopen("lock", "w+");
	if(!flock($lockfp, LOCK_EX | LOCK_NB))
	{
		echo "Another program is already running. Please try again later.";
		return;
	}

	$fp = fopen("tmp/program.bf", "wb");
	fwrite($fp, $_POST["program"]);
	fclose($fp);

	$returnValue = 0;
	system("python bf.py --compile tmp/program.bf tmp/program.c > tmp/compilerOutput.txt", $returnValue);
	if($returnValue != 0)
	{
		$fp = fopen("tmp/compilerOutput.txt", "rb");
		$output = fread($fp, filesize("tmp/compilerOutput.txt"));
		fclose($fp);
		echo $output;
		return;
	}

	system("gcc -O0 -o tmp/program tmp/program.c");
	system("python test.py tmp/program > tmp/testOutput.txt", $returnValue);

	$fp = fopen("tmp/testOutput.txt", "rb");
	$output = fread($fp, filesize("tmp/testOutput.txt"));
	fclose($fp);
	echo $output;

	if($returnValue == 0)
	{
		echo "\nOK\n";
	}
	else
	{
		echo "\nNot OK\n";
	}
}


if($_POST["program"] != "")
{
        echo "<pre>";
	runProgram();
	echo "</pre>\n";
}
?>
</body>
</html>
