const fs = require("fs");
const path = require("path");
const glob = require("glob");
const process = require("process");

const findDirectoryPath = (targetDirectoryName) => {
  const pathToCheck = path.join(process.cwd(), targetDirectoryName);
  const folders = fs
    .readdirSync(pathToCheck, { withFileTypes: true })
    .filter(
      (folder) => folder.isDirectory() && !folder.name.endsWith(".egg-info")
    )
    .map((folder) => ({
      name: folder.name,
      path: path.join(pathToCheck, folder.name),
    }));
  const rpcDirectory = path.join(folders[0].path, "rpc");

  console.log("rpcDirectory", rpcDirectory);
  console.log("folders[0].name", folders[0].name);

  return [rpcDirectory, folders[0].name];
};

const [directoryPath, project_name] = findDirectoryPath("src/");

const outputFile = path.join(process.cwd(), "schemas.json");

function return_json_schema(directoryPath, folder_path, project_name) {
  const folders = fs
    .readdirSync(path.normalize(directoryPath), { withFileTypes: true })
    .filter((folder) => folder.isDirectory())
    .map((folder) => ({
      name: folder.name,
      path: path.join(directoryPath, folder.name),
    }));
  var folders_schemas = {};
  folders.forEach((folder) => {
    console.log("folder", folder);
    if (folder.name == "schemas") {
      console.log("schemas");
      console.log("folder.path", folder.path);
      console.log("test", path.join(folder.path, "/*.json"));
      var jsonFiles = glob.sync(path.join(folder.path, "/*.json"));
      console.log("jsonFiles", jsonFiles);
      var schemas = {};

      jsonFiles.forEach((filePath) => {
        console.log("filePath", filePath);
        try {
          const fileContent = fs.readFileSync(filePath, "utf8");
          var jsonData = JSON.parse(fileContent);
          console.log("jsonData", jsonData);
          var filename = filePath
            .replace(/^.*[\\/]/, "")
            .replace(/\.[^/.]+$/, "");
          var rpc = jsonData["rpc"];
          jsonData["$id"] = project_name + folder_path + "." + rpc;
          schemas[filename] = jsonData;
        } catch (error) {
          console.error(
            `Erreur lors de la lecture du fichier ${filePath}:`,
            error
          );
        }
      });
      folders_schemas = Object.keys(schemas).reduce((acc, key) => {
        const currentSchema = schemas[key];
        const modifiedSchema = {
          $id: path.join(folder_path, currentSchema["$id"]),
          ...currentSchema,
        };
        acc[key] = modifiedSchema;
        return acc;
      }, folders_schemas);
    } else {
      var new_folder_path = folder_path + "/" + folder.name;
      var test = return_json_schema(folder.path, new_folder_path, project_name);
      folders_schemas[folder.name] = test;
    }
  });
  return folders_schemas;
}

if (fs.existsSync(outputFile)) {
  fs.unlinkSync(outputFile);
}

const finalJson = {};
finalJson[project_name] = return_json_schema(directoryPath, "", project_name);

fs.writeFileSync(outputFile, JSON.stringify(finalJson, null, 2));
