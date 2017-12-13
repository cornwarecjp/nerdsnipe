<html>
<body>
Your program:<br>
<form action="." method="POST">
<textarea name="program" cols=80 rows=25><?php
echo $_POST["program"];
?></textarea><br>
<input name="submit" type="submit" value="Submit">
</form>
<?php
if($_POST["program"] != "")
{
	echo "<pre>";

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
	}
	else
	{
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

	echo "</pre>\n";
}
?>
</body>
</html>
