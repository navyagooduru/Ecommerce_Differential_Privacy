from differential_privacy import add_laplace_noise


original_count = 100

protected_count = add_laplace_noise(
    original_count,
    sensitivity=1,
    epsilon=1.0
)

print("Original Count:", original_count)
print("Privacy-Protected Count:", protected_count)