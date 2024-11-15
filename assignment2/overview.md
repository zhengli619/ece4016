# ABR (Adaptive Bitrate) Streaming Project Overview

## 项目结构

本项目旨在实现并测试自适应比特率（ABR）算法，模拟视频流媒体播放过程中在不同网络条件下的适应性。以下是项目各文件夹和文件的作用说明，以及它们在项目中的相互关系。

### 文件树

Files Specification
Below is the file tree of the given environment zip file of this homework:
├───Classes //python classes used in the simulator and grader
├───inputs //inputs files used for single use testing
├───papers //some paper references used for the ABR algorithms
├───tests //tests that grader will run
│ ├───testALThard //test that have a unstable bandwidth that confuses ABR algos
│ ├───testALTsoft //test that have a lot of alternating bandwidth
│ ├───testHD //test that have high quality bandwidth and other params
│ ├───testHDmanPQtrace //test that have high quality bandwidth but low params
│ ├───testPQ //test that have low quality bandwidth and param, will rebuffer.
│ └───...
├───grader.py //python file that graded the ABR algorithm via QOE
├───rand_sizes.py //python helper file use to generate chunk sizes
├───simulator.py //the simulator that generate parameters from text and json files
├───studentcodeExample.py //the file where that contains the student entrypoint
└───studentComm.py //the program the student will call to invoke their ABR algorithm 。

### 文件夹说明

1. **`Classes` 文件夹**：
   - 该文件夹包含用于支持 `simulator.py` 的核心模块，提供了底层功能，如网络追踪处理、缓冲区模拟、评分计算等。可以认为这些文件相当于 `simulator.py` 的支持模块或“头文件”,会在simulator.py中被调用。
   - **主要文件**：
     - `NetworkTrace.py`：处理和解析网络追踪文件的数据，提供网络带宽的模拟。输入为： time 是开始下载的时间，size 是下载的数据大小（单位为字节），输出为是完成下载所需的总时间。
     - `SimBuffer.py`：模拟播放器缓冲区的行为，包括缓冲区填充、消耗和重新缓冲等。输入为：总的buffer size。 sim_chunk_download的输出为：播放时长为playback_time的视频，耗chunks，看耗完之后整个buffer会处于没有任何缓冲块状态多少秒
     - `Scorecard.py`：用于计算 QoE（用户体验质量）评分，帮助评估算法的表现。
     - `simulator_comm.py`：simulator_comm.py 作为 客户端，主动连接 localhost:6000 端口，将模拟状态信（带宽、缓冲状态等）发送到 6000 端口监听的服务器。
     在这个结构中，studentComm.py 充当服务器角色，监听 6000 端口，接收 simulator_comm.py 发来的请求数据。studentComm.py 在接收到状态信息后，会调用学生的比特率算法文件（如 studentcodeExample.py），并基于这些信息做出比特率决策。之后，studentComm.py 会将比特率决策通过套接字返回给 simulator_comm.py。

2. **`inputs` 文件夹**：
   - 该文件夹包含一些单独测试所需的输入文件，可以在开发和调试阶段使用，但在批量评分的流程中可以忽略。
   - **主要文件**：`trace.txt` 文件提供网络带宽信息，`manifest.json` 文件提供视频分块和可用比特率等信息。

3. **`tests` 文件夹**：
   - 包含一组预定义的测试用例，每个测试用例使用一个特定的网络追踪文件和视频配置文件来测试 ABR 算法的适应性。
   - **测试用例结构**：
     - 每个测试用例包含 `manifest.json` 和 `trace.txt` 两个文件，分别描述视频文件的分块信息和网络条件。

### 文件说明

1. **`grader.py`**：
   - 项目的评分入口文件。`grader.py` 会自动遍历 `tests` 文件夹中的每个测试用例，调用 `simulator.py` 并记录学生算法的表现。
   - 输出 `grader.txt` 文件，包含 QoE 得分、缓冲次数和平均比特率等信息，用于量化算法在不同网络条件下的表现。

2. **`simulator.py`**：
   - 项目的核心模拟器程序，负责加载测试用例（包括 `trace.txt` 和 `manifest.json` 文件）并运行学生实现的 ABR 算法。
   - `simulator.py` 调用 `studentComm.py` 来实现与学生算法的交互，提供网络和视频参数，接收比特率决策。

3. **`studentComm.py`**：
   - 作为 `simulator.py` 和学生实现的算法文件（如 `studentcodeExample.py` 或 `studentcode_<学号>.py`）之间的通信接口。
   - `studentComm.py` 从 `simulator.py` 接收网络状态、缓冲区信息等，并将这些信息传递给学生实现的算法，接收比特率选择结果并返回给 `simulator.py`。

4. **`studentcodeExample.py`**：
   - 学生的算法实现文件。`studentcodeExample.py` 是一个示例文件，学生需要创建自己的算法文件（如 `studentcode_<学号>.py`），并在其中实现自适应比特率（ABR）算法。
   - 算法的核心逻辑在于根据网络带宽、缓冲区状态等信息，选择合适的比特率来优化播放体验。

5. **`rand_sizes.py`**：
   - 用于随机生成或修改 `manifest.json` 文件中的分块（chunk）大小信息。
   - 通过正态分布或其他分布生成不同大小的视频块，以模拟真实场景中的不规则视频块大小。这种不规则性可以增加测试的多样性，使得算法测试更具挑战性。

### 使用指南

1. **实现算法**：
   - 在 `studentcode_<学号>.py` 中实现您的 ABR 算法逻辑。
   - 确保 `studentComm.py` 中的入口文件指向您的算法实现文件。

2. **单独测试**：
   - 您可以使用 `inputs` 文件夹中的单独测试文件，在开发和调试过程中手动运行以下命令进行测试：
     python studentComm.py
     python simulator.py inputs/traceHD.txt inputs/manifestHD.json
     
3. **批量评分**：
   - 在完成算法实现后，运行 `python grader.py` 批量测试 `tests` 文件夹中的所有测试用例，并生成 `grader.txt` 文件记录算法表现。

4. **使用 `rand_sizes.py` 生成新的测试用例**：
   - 若需要创建新的测试用例，可以运行 `rand_sizes.py` 来生成不同的视频块大小，并将其保存为新的 `manifest.json` 文件，增加测试的多样性。

### 项目工作流程

1. **`grader.py`** 遍历 `tests` 文件夹中的每个测试用例，调用 `simulator.py`。
2. **`simulator.py`** 加载测试用例的 `trace.txt` 和 `manifest.json` 文件，并通过 `studentComm.py` 调用学生的 ABR 算法。
3. **`studentComm.py`** 将 `simulator.py` 的状态信息传递给学生的算法文件（如 `studentcode_<学号>.py`），并接收比特率决策。
4. **学生算法文件** 使用 ABR 逻辑，根据当前网络和缓冲状态选择比特率，返回给 `simulator.py`。
5. **评分结果** 通过 `grader.txt` 输出，评估算法在各种网络条件下的表现。

### 备注

- 请确保所有文件格式和命名符合要求，以确保评分程序能够正常运行。
- `inputs` 文件夹可用于调试阶段，`tests` 文件夹为最终评分时的测试用例。
- 若需使用额外 Python 库，请在提交时附上 `req.txt` 环境文件，以便评审者配置环境。

