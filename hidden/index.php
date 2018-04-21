<html>
<body>
Note: there is a solution, with SHA256sum 083215477510be65f0bac53e84a531e826db4e3873f261dba2cdfc362843a375.
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
	$tmpdir = "this_is_censored_in_the_public_Git_version";

	$wouldBlock = false;
	$lockfp = fopen("lock", "w+");
	if(!flock($lockfp, LOCK_EX | LOCK_NB))
	{
		echo "Another program is already running. Please try again later.";
		return;
	}

	$fp = fopen("$tmpdir/program.bf", "wb");
	fwrite($fp, $_POST["program"]);
	fclose($fp);

	$returnValue = 0;
	system("python bf.py --compile $tmpdir/program.bf $tmpdir/program.c > $tmpdir/compilerOutput.txt", $returnValue);
	if($returnValue != 0)
	{
		$fp = fopen("$tmpdir/compilerOutput.txt", "rb");
		$output = fread($fp, filesize("$tmpdir/compilerOutput.txt"));
		fclose($fp);
		echo $output;
		return;
	}

	system("gcc -O0 -o $tmpdir/program $tmpdir/program.c");
	system("python test.py $tmpdir $tmpdir/program > $tmpdir/testOutput.txt", $returnValue);

	$fp = fopen("$tmpdir/testOutput.txt", "rb");
	$output = fread($fp, filesize("$tmpdir/testOutput.txt"));
	fclose($fp);
	echo $output;

	if($returnValue == 0)
	{
		echo "\nOK";
		echo "\nYou gained access to the <a href=\"2d7e473fae0c3fb887c5906166ee107a8dd49627218f6159bbdc46d35026eae1.html\">Next page</a>.";
	}
	else
	{
		echo "\nNot OK";
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
