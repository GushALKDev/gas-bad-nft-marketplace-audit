methods {
    function totalSupply() external returns uint256 envfree;
    function mint() external;
    function balanceOf(address) external returns uint256 envfree;
    function name() external returns string envfree;
    function symbol() external returns string envfree;
}

// invariant totalSupplyIsNotNegative()
//     totalSupply() >= 0;

rule minting_mint_on_nft() {
    // Arrange: Capture the initial total supply and balance of the minter
    env e;
    address minter;

    uint256 MAX_UINT256 = 2^256 - 1;

    require e.msg.value == 0;
    require e.msg.sender == minter;

    // We use mathint because uint256 has a cap and we want to avoid overflow issues in our assertions
    mathint initialBalance = balanceOf(minter);

    // Prevent overflow: exclude the case where initialBalance is already at the max value
    require initialBalance < MAX_UINT256;

    // Act: Call the mint function
    mint(e);

    // Assert: Capture the new total supply and assert that the new supply is exactly one more than the initial supply;
    assert to_mathint(balanceOf(minter)) == initialBalance + 1, "User balance should increase by 1 after minting";
}

// Parametric rule
// This rule ensures that totalSupply does not change for any method except those that explicitly modify state or return dynamic types.
// We filter out mint() because it modifies state, and name()/symbol() because they return string and Certora has issues with dynamic types in parametric rules.
rule no_change_total_supply(method f)
    filtered { 
        f -> f.selector != sig:mint().selector &&
             f.selector != sig:name().selector &&
             f.selector != sig:symbol().selector
    }
{
    uint256 totalSupplyBefore = totalSupply();
    env e;
    calldataarg arg;
    f(e, arg);
    assert totalSupply() == totalSupplyBefore, "Total supply should not change";
}