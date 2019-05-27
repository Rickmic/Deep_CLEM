function doSomething(input, output, filename) {
	open(input + filename);
	saveAs("Tiff", output + filename);
	close();
}
input = "/home/s353960/CSBDeep/Rem_resz/";
output = "/home/s353960/CSBDeep/Rem_tif/";

list = getFileList(input);
for (i = 0; i < list.length; i++)
        doSomething(input, output, list[i]);
