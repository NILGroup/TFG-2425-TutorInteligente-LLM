// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <map>
#include <filesystem>

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "LocalFileDatabaseActor.generated.h"

using namespace std;

USTRUCT(BlueprintType)
struct FQueryData
{
	GENERATED_USTRUCT_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	FString tableName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	FString query;

	FQueryData() {};
};

/**
 * 
 */
UCLASS()
class RADIATIONROOM_API ALocalFileDatabaseActor: public AActor
{
	GENERATED_BODY()

private:
	FString _path;
	TMap<FString, TArray<FString>> _querys;

	string FStringToString(FString s);
	FString StringToFString(string s);

	int32 GetLastEventId(fstream& file);
	int32 GetLastEventId(FString tableName);

	string GetFilePath(FString tableName);
	FQueryData GetDataFromQuery(FString data);
	bool TableExists(FString tableName);
	pair<bool, int> UserExistsInDatabase(FString userName);

public:

	UFUNCTION(BlueprintCallable, category = "LocalFileDatabaseActor")
	void Init();

	UFUNCTION(BlueprintCallable, category = "LocalFileDatabaseActor")
	void CreateNewDirectoryAndSetPath(FString path, FString directoryName);

	UFUNCTION(BlueprintCallable, category = "LocalFileDatabaseActor")
	void SetPath(FString path);

	UFUNCTION(BlueprintCallable, category = "LocalFileDatabaseActor")
	void CreateTable(FString tableName, TArray<FString> header);

	UFUNCTION(BlueprintCallable, category = "LocalFileDatabaseActor")
	void ReadTable(FString tableName, bool hasHeader,
		UPARAM(DisplayName = "Header") FString &header, UPARAM(DisplayName = "Data") TArray<FString> &data);

	UFUNCTION(BlueprintCallable, category = "LocalFileDatabaseActor")
	void AddOneQuery(FString data);

	UFUNCTION(BlueprintCallable, category = "LocalFileDatabaseActor")
	void AddMultiplesQuerys(TArray<FString> data);

	UFUNCTION(BlueprintCallable, category = "LocalFileDatabaseActor")
	void InsertQuerysToTable();	

	UFUNCTION(BlueprintCallable, category = "LocalFileDatabaseActor")
	void InsertUserToTable(FString userName, FString data);

	UFUNCTION(BlueprintCallable, BlueprintPure, category = "LocalFileDatabaseActor")
	bool AreThereQuerysToInsert();

	UFUNCTION(BlueprintCallable, category = "LocalFileDatabaseActor")
	int32 GetUserIdByName(FString userName);

	// Callbacks
	UFUNCTION(BlueprintImplementableEvent, Category = "LocalFileDatabaseActor")
	void OnQuerysInserted();
};
