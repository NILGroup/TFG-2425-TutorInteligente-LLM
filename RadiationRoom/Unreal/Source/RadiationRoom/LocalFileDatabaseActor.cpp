// Fill out your copyright notice in the Description page of Project Settings.


#include "LocalFileDatabaseActor.h"

string ALocalFileDatabaseActor::FStringToString(FString s)
{
	return string(TCHAR_TO_UTF8(*s));
}

FString ALocalFileDatabaseActor::StringToFString(string s)
{
	return UTF8_TO_TCHAR(s.c_str());
}


string ALocalFileDatabaseActor::GetFilePath(FString tableName)
{
	string auxFilename = FStringToString(tableName);
	FString result = _path + "/" + tableName + ".csv";

	return FStringToString(result);
}

FQueryData ALocalFileDatabaseActor::GetDataFromQuery(FString data) {
	/*
INSERT INTO PHD_tutorial_DB.user_radiation_events (user_id, scenario_type, dose_rate, dose_absortion, event_position, event_datetime) VALUES(2, "Develop", "0.084817", "0.0", "(-14 021,768;9 922,017)", "2024-1-17 14:18:57")
 */
	string auxQuery = FStringToString(data);

	string tableName = auxQuery;
	string sToRemove = "INSERT INTO ";
	tableName.erase(0, sToRemove.size());
	tableName.erase(0, tableName.find(".") + 1);
	tableName.erase(tableName.find(" ("), tableName.size() - 1);

	string values = auxQuery;
	values.erase(0, values.find("VALUES"));
	sToRemove = "VALUES(";
	values.erase(0, sToRemove.size());
	values.erase(values.size() - 1, values.size());

	std::string::size_type n = 0;
	while ((n = values.find(", ", n)) != string::npos) {
		values.replace(n, 2, ",");
	}

	FQueryData queryData = FQueryData();
	queryData.tableName = StringToFString(tableName);
	queryData.query = StringToFString(values);

	return queryData;
}

int32 ALocalFileDatabaseActor::GetLastEventId(fstream& file)
{
	string lastLine;

	file.seekg(-1, ios_base::end);                // go to one spot before the EOF

	bool keepLooping = true;
	while (keepLooping) {
		char ch;
		file.get(ch);                            // Get current byte's data

		if ((int)file.tellg() <= 1) {             // If the data was at or before the 0th byte
			file.seekg(0);                       // The first line is the last line
			keepLooping = false;                // So stop there
		}
		else if (ch == '\n') {                   // If the data was a newline
			keepLooping = false;                // Stop at the current position.
		}
		else {                                  // If the data was neither a newline nor at the 0 byte
			file.seekg(-2, ios_base::cur);        // Move to the front of that data, then to the front of the data before it
		}
	}

	//string lastLine;
	getline(file, lastLine);                      // Read the current line
	file.clear();

	string firstValue = lastLine.substr(0, lastLine.find(","));
	
	return (firstValue == "id") ? 0 : (stoi(firstValue) + 1);
}

int32 ALocalFileDatabaseActor::GetLastEventId(FString tableName)
{
	fstream file;
	file.open(GetFilePath(tableName), fstream::in);

	return GetLastEventId(file);
}

void ALocalFileDatabaseActor::SetPath(FString path)
{
	_path = path;
}

bool ALocalFileDatabaseActor::TableExists(FString tableName)
{
	fstream file;
	file.open(GetFilePath(tableName), fstream::in);

	if (file) return true;
	else return false;
}

pair<bool, int> ALocalFileDatabaseActor::UserExistsInDatabase(FString userName)
{
	fstream file;
	file.open(GetFilePath("users"), fstream::in);
	int tryNum = 0;


	if (file) {
		string line, userLine;
		bool usersExists = false;
		getline(file, line);
		while (getline(file, line)) {
			//UE_LOG(LogTemp, Warning, TEXT("CreateUser: %s"), *StringToFString(line));
			if (StringToFString(line).Contains(userName)) {
				usersExists = true;
				userLine = line;
				//UE_LOG(LogTemp, Warning, TEXT("Left: %s"), *left);
			}
		}
		file.close();

		if (usersExists) {
			FString left;
			FString right;
			StringToFString(userLine).Split(TEXT("_"), &left, &right);
			right.Split(TEXT(","), &left, &right);
			left.RemoveAt(left.Len() - 1, 1);
			tryNum = stoi(FStringToString(left)) + 1;
		}

		return pair<bool, int>(usersExists, tryNum);
	}

	return pair<bool, int>(false, 0);
}

void ALocalFileDatabaseActor::Init()
{
	_querys = TMap<FString, TArray<FString>>();
}

void ALocalFileDatabaseActor::CreateNewDirectoryAndSetPath(FString path, FString directoryName)
{
	filesystem::create_directory(FStringToString(path));
	string auxPath = FStringToString(path) + "/" + FStringToString(directoryName);
	filesystem::create_directory(auxPath);
	SetPath(StringToFString(auxPath));
}

void ALocalFileDatabaseActor::CreateTable(FString tableName, TArray<FString> header)
{
	if (!TableExists(tableName)) {
		fstream file;
		file.open(GetFilePath(tableName), fstream::out);

		int s_index = 0;
		while (s_index < header.Num()) {
			file << FStringToString(*header[s_index]);

			//UE_LOG(LogTemp, Warning, TEXT("CreateTable: %s"), *header[s_index]);

			if (s_index < header.Num() - 1) file << ',';

			s_index++;
		}

		file.close();
	}	

	_querys.Add(tableName, TArray<FString>());
}


void ALocalFileDatabaseActor::ReadTable(FString tableName, bool hasHeader, 
	FString& header, TArray<FString>& data)
{
	fstream file;
	file.open(GetFilePath(tableName), fstream::in);


	if (file) {
		TArray<FString> rows;
		string line;
		while (getline(file, line)) {
			rows.Add(line.c_str());
		}
		file.close();

		header = "";
		if (hasHeader) {
			header = rows[0];
			rows.RemoveAt(0);
		}
		data = rows;
	}
}

void ALocalFileDatabaseActor::AddOneQuery(FString data)
{
	FQueryData queryData = GetDataFromQuery(data);

	_querys[queryData.tableName].Add(queryData.query);

	//UE_LOG(LogTemp, Warning, TEXT("AddOneQuery: %s"), *queryData.query);
}

void ALocalFileDatabaseActor::AddMultiplesQuerys(TArray<FString> data) {

	for (FString query : data) {
		AddOneQuery(query);
	}
}

void ALocalFileDatabaseActor::InsertQuerysToTable() {	

	for (TPair<FString, TArray<FString>>& queryBlock : _querys) {
		fstream file;
		file.open(GetFilePath(queryBlock.Key));
		if (file) {

			int32 lastEventId = GetLastEventId(file);

			for (FString query : queryBlock.Value)
			{
				FString newQuery = FString::FromInt(lastEventId)+ "," + query;
				//UE_LOG(LogTemp, Warning, TEXT("InsertQuerysToTable: %s -- %s"), *queryBlock.Key, *newQuery);

				file << '\n';
				file << FStringToString(newQuery);

				lastEventId++;
			}

			queryBlock.Value.Empty();
		}

		file.close();
	}

	OnQuerysInserted();
}

void ALocalFileDatabaseActor::InsertUserToTable(FString userName, FString data)
{
	//pair<bool, int> exist_user_info = UserExistsInDatabase(userName);

	//string newUserName = FStringToString(userName) + "_" + to_string(exist_user_info.second);
	FQueryData queryData = GetDataFromQuery(data);

	fstream file;
	file.open(GetFilePath(queryData.tableName));
	if (file) {

		int32 lastEventId = GetLastEventId(file);

		FString left;
		FString right;
		queryData.query.Split(TEXT(","), &left, &right);

		FString newQuery = FString::FromInt(lastEventId) + "," + '"' + userName + '"' + "," + right;
		//FString newQuery = FString::FromInt(lastEventId) + "," + '"' + StringToFString(newUserName) + '"' + "," + right;

		// Hipótesis 10 del doctorado: Si quito este "print" no se envían las cosas a la base de datos.
		//UE_LOG(LogTemp, Warning, TEXT("InsertUser: %s"), *newQuery);

		file << '\n';
		file << FStringToString(newQuery);

		lastEventId++;

	}

	file.close();

}

bool ALocalFileDatabaseActor::AreThereQuerysToInsert()
{
	
	if (_querys.IsEmpty()) return false;
	else {
		bool result = false;
		for (TPair<FString, TArray<FString>>& queryBlock : _querys) {
			if (!queryBlock.Value.IsEmpty()) {
				result = true;
				break;
			}
		}
		return result;
	}	
}

int32 ALocalFileDatabaseActor::GetUserIdByName(FString userName)
{
	int32 userId = -1;

	fstream file;
	file.open(GetFilePath("users"), fstream::in);

	if (file) {
		string line, userLine;
		bool usersExists = false;
		getline(file, line);
		while (getline(file, line)) {
			if (StringToFString(line).Contains(userName)) {
				usersExists = true;
				userLine = line;
			}
		}
		file.close();

		return stoi(userLine.substr(0, userLine.find(",")));
	}

	return -1;
}
