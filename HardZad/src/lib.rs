use pyo3::prelude::*;
use ndarray::Array1;

/// Форматирует сумму чисел, используя Rust
#[pyfunction]
fn fast_sum(numbers: Vec<f64>) -> PyResult<f64> {
    let arr = Array1::from_vec(numbers);
    Ok(arr.sum())
}

/// A Python module implemented in Rust.
#[pymodule]
fn my_rust_core(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(fast_sum, m)?)?;
    Ok(())
}