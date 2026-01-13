def main():
    print("Running build command...")
    # 在这里可以添加任何构建步骤
    # 对于FastAPI应用，通常不需要特殊的构建步骤
    with open("build.txt", "w") as f:
        f.write("BUILD_COMMAND")


if __name__ == "__main__":
    main()